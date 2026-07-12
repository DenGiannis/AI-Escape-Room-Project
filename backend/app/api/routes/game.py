from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.graph import (
    _append_memory,
    _convert_to_lc_messages,
    _load_memory,
    _save_memory,
    answer_player_question,
    get_hint as agent_get_hint,
    interpret_action,
    judge_truth_answer,
    narrate_result,
    narrate_off_topic,
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
    welcome = (
        f"Welcome, {game.player_name}. I am Athena, guide of the Library of Alexandria. "
        "You find yourself in the entrance hall, and a heavy bronze door blocks the way "
        "deeper inside.\n\n"
        "A few things before we begin:\n"
        "- **examine** something to look at it closely (e.g. \"examine the shelves\")\n"
        "- **take** an item once you've found it (e.g. \"take the seal\")\n"
        "- **use** an item or object to interact with it (e.g. \"use the iron key on the door\")\n"
        "- speak naturally — I will do my best to understand what you mean\n"
        "- ask for a **hint** any time you feel stuck\n\n"
        "You stand in the entrance hall of the Library of Alexandria. Marble columns rise "
        "to a vaulted ceiling painted with constellations. Shafts of golden sunlight fall "
        "across long tables covered in open scrolls. At the far end, a heavy bronze door "
        "bears the inscription: 'Only those who carry the three seals of knowledge may pass.' "
        "What do you do?"
    )
    return GameSessionPublic(
        session_id=game.id,
        player_name=game.player_name,
        current_room=game.current_room,
        inventory=game.get_inventory(),
        solved_puzzles=game.get_solved_puzzles(),
        is_escaped=game.is_escaped,
        message=welcome,
    )


@router.post("/action", response_model=ActionResponse)
async def game_action(body: ActionRequest, session: SessionDep):
    game = _get_session_or_404(body.session_id, session)
    if game.is_escaped:
        raise HTTPException(status_code=400, detail="Game already completed")
    room_overview_targets = {"room", "area", "around", "surroundings"}
    # 1. Parse natural language → {action_type, target}
    parsed = await interpret_action(
        player_input=body.input,
        room=game.current_room,
        inventory=game.get_inventory(),
        found_items=game.get_found_items(),
    )
    action_type = parsed["action_type"]
    target = parsed["target"]

    # 2. Load memory and capture room before any state mutation
    memory = _load_memory(game)
    lc_history = _convert_to_lc_messages(memory)
    room_before_action = game.current_room

    # 3. Off-topic / chit-chat / inappropriate input never touches game state —
    #    just a short in-character redirect back to the puzzle.
    if action_type == "off_topic":
        narration = await narrate_off_topic(
            player_input=body.input,
            room=room_before_action,
            history=lc_history,
        )
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

    # 3b. In-world question → tool-calling agent (decides whether to call RAG),
    #     grounded in the knowledge base. Never mutates game state.
    if action_type == "ask":
        narration = await answer_player_question(
            player_input=body.input,
            room=room_before_action,
            history=lc_history,
        )
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

    # 4. Special case: player is answering the vault's truth question
    if action_type == "answer_truth":
        is_honest = await judge_truth_answer(body.input)
        target = "true" if is_honest else "false"

    # 5. Run game logic (mutates game in-place)
    result = process_action(game, action_type, target)

    # 6. Narrate the result as Athena, with conversation history for context.
    #    Some results are shown verbatim to guarantee no embellishment: full room
    #    overviews, and any result process_action marks with "verbatim" (e.g. the
    #    contents of the desk drawer, where the exact items present must not drift).
    show_verbatim = result.get("verbatim") or (
        action_type == "examine" and target in room_overview_targets
    )
    if show_verbatim:
        narration = result["raw_result"]
    else:
        narration = await narrate_result(
            raw_result=result["raw_result"],
            player_input=body.input,
            room=room_before_action,
            history=lc_history,
        )

    # 7. Persist memory and game changes
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
        found_items=game.get_found_items(),
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
