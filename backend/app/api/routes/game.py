from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.graph import (
    _append_memory,
    _convert_to_lc_messages,
    _load_memory,
    _save_memory,
    get_hint as agent_get_hint,
    interpret_action,
    judge_truth_answer,
    narrate_result,
)
from app.api.deps import SessionDep
from app.game_logic import process_action
from app.models import GameSession

router = APIRouter(prefix="/game", tags=["game"])


# --- Request / Response schemas ---

class StartGameRequest(BaseModel):
    player_name: str


class GameSessionPublic(BaseModel):
    session_id: str
    player_name: str
    current_room: str
    inventory: list[str]
    solved_puzzles: list[str]
    is_escaped: bool
    message: str


class ActionRequest(BaseModel):
    session_id: str
    input: str


class ActionResponse(BaseModel):
    session_id: str
    narration: str
    current_room: str
    inventory: list[str]
    solved_puzzles: list[str]
    is_escaped: bool


class HintRequest(BaseModel):
    session_id: str
    puzzle_id: str | None = None


class HintResponse(BaseModel):
    session_id: str
    hint: str
    hint_count: int


class InventoryResponse(BaseModel):
    session_id: str
    inventory: list[str]
    found_items: list[str]


class SummaryResponse(BaseModel):
    session_id: str
    player_name: str
    current_room: str
    inventory: list[str]
    solved_puzzles: list[str]
    found_items: list[str]
    hint_count: int
    is_escaped: bool


# --- Helpers ---

def _get_session_or_404(session_id: str, session: SessionDep) -> GameSession:
    game = session.get(GameSession, session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game session not found")
    return game


# --- Endpoints ---

@router.post("/start", response_model=GameSessionPublic)
def start_game(body: StartGameRequest, session: SessionDep):
    game = GameSession(player_name=body.player_name)
    session.add(game)
    session.commit()
    session.refresh(game)
    return GameSessionPublic(
        session_id=game.id,
        player_name=game.player_name,
        current_room=game.current_room,
        inventory=game.get_inventory(),
        solved_puzzles=game.get_solved_puzzles(),
        is_escaped=game.is_escaped,
        message=f"Welcome, {game.player_name}! You find yourself locked in a strange room. What do you do?",
    )


@router.post("/action", response_model=ActionResponse)
async def game_action(body: ActionRequest, session: SessionDep):
    game = _get_session_or_404(body.session_id, session)
    if game.is_escaped:
        raise HTTPException(status_code=400, detail="Game already completed")

    # 1. Parse natural language → {action_type, target}
    parsed = await interpret_action(
        player_input=body.input,
        room=game.current_room,
        inventory=game.get_inventory(),
        found_items=game.get_found_items(),
    )
    action_type = parsed["action_type"]
    target = parsed["target"]

    # 2. Special case: player is answering the vault's truth question
    if action_type == "answer_truth":
        is_honest = await judge_truth_answer(body.input)
        target = "true" if is_honest else "false"

    # 3. Load memory and capture room before game logic mutates state
    memory = _load_memory(game)
    lc_history = _convert_to_lc_messages(memory)
    room_before_action = game.current_room

    # 4. Run game logic (mutates game in-place)
    result = process_action(game, action_type, target)

    # 5. Narrate the result as Athena, with conversation history for context
    narration = await narrate_result(
        raw_result=result["raw_result"],
        player_input=body.input,
        room=room_before_action,
        history=lc_history,
    )

    # 6. Persist memory and game changes
    new_memory = _append_memory(memory, body.input, narration)
    _save_memory(game, new_memory)
    session.add(game)
    session.commit()
    session.refresh(game)

    return ActionResponse(
        session_id=game.id,
        narration=narration,
        current_room=game.current_room,
        inventory=game.get_inventory(),
        solved_puzzles=game.get_solved_puzzles(),
        is_escaped=game.is_escaped,
    )


@router.post("/hint", response_model=HintResponse)
async def get_hint(body: HintRequest, session: SessionDep):
    game = _get_session_or_404(body.session_id, session)

    hint = await agent_get_hint(
        room=game.current_room,
        solved_puzzles=game.get_solved_puzzles(),
        inventory=game.get_inventory(),
        hint_count=game.hint_count,
        puzzle_id=body.puzzle_id,
    )
    game.hint_count += 1
    session.add(game)
    session.commit()
    session.refresh(game)
    return HintResponse(session_id=game.id, hint=hint, hint_count=game.hint_count)


@router.get("/inventory/{session_id}", response_model=InventoryResponse)
def get_inventory(session_id: str, session: SessionDep):
    game = _get_session_or_404(session_id, session)
    return InventoryResponse(
        session_id=game.id,
        inventory=game.get_inventory(),
        found_items=game.get_found_items(),
    )


@router.get("/summary/{session_id}", response_model=SummaryResponse)
def get_summary(session_id: str, session: SessionDep):
    game = _get_session_or_404(session_id, session)
    return SummaryResponse(
        session_id=game.id,
        player_name=game.player_name,
        current_room=game.current_room,
        inventory=game.get_inventory(),
        solved_puzzles=game.get_solved_puzzles(),
        found_items=game.get_found_items(),
        hint_count=game.hint_count,
        is_escaped=game.is_escaped,
    )
