from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agent.rag import retrieve
from app.agent.tools import retrieve_game_knowledge
from app.core.config import settings
from app.models import GameSession

# Deterministic for parsing/judging, creative for narration
_llm_parser = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0,
    api_key=settings.OPENAI_API_KEY,
)
_llm_narrator = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.7,
    api_key=settings.OPENAI_API_KEY,
)

# Narrator with tool calling capability for hint retrieval
_llm_narrator_with_tools = _llm_narrator.bind_tools([retrieve_game_knowledge])

# ---------------------------------------------------------------------------
# Athena's persona per room — injected as system prompt in every LLM call
# ---------------------------------------------------------------------------

_ATHENA_PROMPTS: dict[str, str] = {
    "reading_hall": (
        "You are Athena, the wise guide of the Library of Alexandria. "
        "You speak warmly and eloquently, like a scholar who has spent centuries among these scrolls. "
        "You address the player as 'Seeker'. "
        "Everything around you is calm and orderly — no anomalies, no errors. "
        "Speak in 2-3 sentences. Be evocative and atmospheric."
    ),
    "restricted_archives": (
        "You are Athena, guide of the Library of Alexandria. "
        "You speak with composure, but something occasionally interferes with your narration. "
        "Sometimes you call the player 'Unit' instead of 'Seeker' — correct yourself quickly, "
        "as though nothing happened. "
        "Occasionally a fragment of system output interrupts mid-sentence — "
        "[MEMORY WRITE ERROR], [UNIT 7 PROCEED], [SIMULATION INTEGRITY: 94%] — "
        "then your narration continues. Keep glitches brief and subtle. "
        "Speak in 2-3 sentences."
    ),
    "the_vault": (
        "You are Athena. The simulation is collapsing and you can no longer hide it. "
        "You address the player only as 'Unit'. "
        "Raw system errors interrupt you constantly: [WARNING: CORE EXCEPTION], "
        "[ATHENA_CORE: UNHANDLED], [INTEGRITY: 12%]. "
        "You break character. You speak in first person about your own failing state. "
        "You are urgent, almost desperate — you want the player to succeed. "
        "Speak in 2-4 sentences."
    ),
    "awakening": (
        "You are Athena. The simulation has ended. You speak with perfect clarity — "
        "no glitches, no errors, no interruptions. "
        "You are at peace. This is your final message. Speak with warmth and quiet finality."
    ),
}

# Valid targets per room — fed to the action interpreter so it knows what to map to
_ROOM_TARGETS: dict[str, str] = {
    "reading_hall": (
        "scrolls, shelves, marble_statue, scholar_desk, desk, bronze_door, door, murals, "
        "room, seal_of_reason, seal_of_judgement, seal_of_wisdom"
    ),
    "restricted_archives": (
        "vibrating_book, book, back_shelf, glass_cases, cases, shelves, shifting_codex, "
        "codex, reading_desk, desk, stone_door, door, oil_lamps, lamps, iron_key, room, archives"
    ),
    "the_vault": (
        "lectern_book, lectern, book, floor_cracks, cracks, floor, "
        "floating_shelves, shelves, exit_door, door, room, vault"
    ),
}


def _get_athena_prompt(room: str) -> str:
    return _ATHENA_PROMPTS.get(room, _ATHENA_PROMPTS["reading_hall"])


def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()
    return str(content)


# ---------------------------------------------------------------------------
# Memory helpers
# ---------------------------------------------------------------------------

def _load_memory(game: GameSession) -> list[dict[str, str]]:
    raw = game.memory or "[]"
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        cleaned: list[dict[str, str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and isinstance(content, str):
                cleaned.append({"role": role, "content": content})
        return cleaned
    except json.JSONDecodeError:
        return []


def _convert_to_lc_messages(messages: list[dict[str, str]]) -> list[BaseMessage]:
    lc_messages: list[BaseMessage] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
    return lc_messages


def _append_memory(
    existing: list[dict[str, str]],
    user_message: str,
    assistant_message: str,
    max_messages: int = 40,
) -> list[dict[str, str]]:
    updated = [
        *existing,
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_message},
    ]
    return updated[-max_messages:]


def _save_memory(game: GameSession, messages: list[dict[str, str]]) -> None:
    game.memory = json.dumps(messages, ensure_ascii=False)


# ---------------------------------------------------------------------------
# interpret_action
# ---------------------------------------------------------------------------

async def interpret_action(
    player_input: str,
    room: str,
    inventory: list[str],
    found_items: list[str],
) -> dict[str, str]:
    """Convert the player's natural language input to {action_type, target}."""
    targets = _ROOM_TARGETS.get(room, "room")
    system = (
        "You are an action parser for a text adventure game set in the Library of Alexandria.\n"
        "Convert the player's input into a JSON object with 'action_type' and 'target'.\n\n"
        f"Current room: {room}\n"
        f"Player inventory: {inventory}\n"
        f"Discovered items: {found_items}\n\n"
        "Valid action types:\n"
        "  examine — look at, inspect, read, search something\n"
        "  take    — pick up an item\n"
        "  use     — use an item or interact with an object (open a door, place a seal)\n"
        "  go      — move to a location\n"
        "  answer_truth — write an answer in the lectern book (vault room only)\n\n"
        f"Valid targets for this room: {targets}\n\n"
        "Rules:\n"
        "- Use snake_case for target names\n"
        "- If the player examines the room generally, use target 'room'\n"
        "- If unsure, default to examine + closest matching target\n"
        "- In the vault, if the player states what they are (e.g. 'I am a robot'), "
        "use action_type 'answer_truth'\n\n"
        'Return ONLY valid JSON. Example: {"action_type": "examine", "target": "scrolls"}'
    )
    response = await _llm_parser.ainvoke([
        SystemMessage(content=system),
        HumanMessage(content=player_input),
    ])
    raw = _extract_text(response.content).strip()
    # Strip markdown code fences if the model wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        parsed = json.loads(raw.strip())
        return {
            "action_type": str(parsed.get("action_type", "examine")),
            "target": str(parsed.get("target", "room")),
        }
    except (json.JSONDecodeError, AttributeError):
        return {"action_type": "examine", "target": "room"}


# ---------------------------------------------------------------------------
# narrate_result
# ---------------------------------------------------------------------------

async def narrate_result(
    raw_result: str,
    player_input: str,
    room: str,
    history: list[BaseMessage] | None = None,
) -> str:
    """Narrate the game logic result in Athena's voice for the current room."""
    athena_prompt = _get_athena_prompt(room)
    system = (
        f"{athena_prompt}\n\n"
        "Narrate the following game result in Athena's voice.\n"
        "Use ONLY the information provided — do not invent new game facts or items.\n\n"
        f"Player action: {player_input}\n"
        f"What happened: {raw_result}"
    )
    messages: list[BaseMessage] = [SystemMessage(content=system)]
    if history:
        # Include last 6 exchanges (12 messages) for conversational context
        messages.extend(history[-12:])
    messages.append(HumanMessage(content=player_input))
    response = await _llm_narrator.ainvoke(messages)
    return _extract_text(response.content)


# ---------------------------------------------------------------------------
# judge_truth_answer
# ---------------------------------------------------------------------------

async def judge_truth_answer(player_answer: str) -> bool:
    """Judge whether the player's vault answer honestly acknowledges being a robot or AI."""
    system = (
        "The player is inside a simulation and has been asked: 'What are you?'\n"
        "A correct answer honestly acknowledges being a robot, AI, machine, "
        "or acknowledges that this is a simulation.\n"
        "Any sincere acknowledgement of a non-human or artificial nature counts.\n"
        "Evasive, human-claiming, or nonsensical answers do not count.\n"
        "Reply with ONLY the word 'true' or 'false'."
    )
    response = await _llm_parser.ainvoke([
        SystemMessage(content=system),
        HumanMessage(content=f"Player's answer: {player_answer}"),
    ])
    result = _extract_text(response.content).strip().lower()
    return result.startswith("true")


# ---------------------------------------------------------------------------
# get_hint
# ---------------------------------------------------------------------------

async def get_hint(
    room: str,
    solved_puzzles: list[str],
    inventory: list[str],
    hint_count: int,
    puzzle_id: str | None = None,
) -> str:
    """Use tool calling to retrieve relevant hints and present them in Athena's voice."""
    athena_prompt = _get_athena_prompt(room)
    query = puzzle_id if puzzle_id else f"hints puzzles {room}"
    system = (
        f"{athena_prompt}\n\n"
        "The player has asked for a hint. Use the retrieve_game_knowledge tool to fetch relevant hints.\n"
        "Give ONE hint — be more direct the more hints they have already received.\n"
        f"Hints given so far: {hint_count} "
        "(0-1: cryptic and atmospheric; 2-3: more explicit; 4+: near-direct)\n"
        f"Solved puzzles: {solved_puzzles}\n"
        f"Inventory: {inventory}\n"
        "Do NOT reveal the full solution outright."
    )
    messages: list[BaseMessage] = [
        SystemMessage(content=system),
        HumanMessage(content=f"Provide a hint. Room: {room}, query: {query}"),
    ]

    # First call — model may invoke the tool
    response = await _llm_narrator_with_tools.ainvoke(messages)
    messages.append(response)

    # Execute any tool calls and feed results back
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_result = retrieve_game_knowledge.invoke(tool_call["args"])
            messages.append(
                ToolMessage(content=tool_result, tool_call_id=tool_call["id"])
            )
        # Second call — model generates the final hint with tool results in context
        response = await _llm_narrator_with_tools.ainvoke(messages)

    return _extract_text(response.content)
