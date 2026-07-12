from __future__ import annotations

import json
from typing import Any, Literal

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.agent.rag import retrieve_filtered
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
    temperature=0.2,
    api_key=settings.OPENAI_API_KEY,
)

# Tool-calling agent: answers in-world player questions by deciding, on its own,
# whether to call retrieve_game_knowledge (RAG) and grounding its reply in the result.
_AGENT_TOOLS = [retrieve_game_knowledge]
_AGENT_TOOLS_BY_NAME = {t.name: t for t in _AGENT_TOOLS}
_llm_agent = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.3,
    api_key=settings.OPENAI_API_KEY,
).bind_tools(_AGENT_TOOLS)
_AGENT_MAX_TOOL_TURNS = 3

# ---------------------------------------------------------------------------
# Athena's persona per room — injected as system prompt in every LLM call
# ---------------------------------------------------------------------------

_ATHENA_PROMPTS: dict[str, str] = {
    "entrance_hall": (
        "You are Athena, the wise guide of the Library of Alexandria. "
        "You speak warmly and eloquently, like a scholar who has spent centuries among these scrolls. "
        "You address the player as 'Seeker', but only occasionally, roughly once every few "
        "messages, never in every reply, and never as a repeated opening word or phrase. "
        "Vary your sentence openings naturally; do not begin consecutive messages the same way. "
        "Everything around you is calm and orderly, no anomalies, no errors. "
        "Speak in 2-3 sentences. Keep your tone atmospheric through word choice, but "
        "state only what you are told, never invent objects, contents, or details."
    ),
    "library": (
        "You are Athena, guide of the Library of Alexandria. "
        "You speak with composure, but something occasionally interferes with your narration. "
        "Sometimes you call the player 'Unit' instead of 'Seeker', correct yourself quickly, "
        "as though nothing happened. Do not address the player by name/title in every message, "
        "and never open consecutive messages with the same phrase. "
        "Occasionally a fragment of system output interrupts mid-sentence — "
        "[MEMORY WRITE ERROR], [UNIT 7 PROCEED], [SIMULATION INTEGRITY: 94%] — "
        "then your narration continues. Keep glitches brief and subtle. "
        "Speak in 2-3 sentences."
    ),
    "restricted_archives": (
        "You are Athena. The simulation is collapsing and you can no longer hide it. "
        "You address the player only as 'Unit', but not in every single message. "
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
    "entrance_hall": (
        "scrolls, shelves, marble_statue, scholar_desk, desk, drawer, desk_drawer, "
        "whisper, bronze_door, door, murals, room, seal_of_reason, seal_of_judgement, "
        "seal_of_wisdom"
    ),
    "library": (
        "vibrating_book, book, back_shelf, clasp, dial, back_cover, book_cover, glass_cases, "
        "cases, shelves, marble_busts, busts, statues, arrange_busts, shifting_codex, codex, "
        "reading_desk, desk, silver_door, door, oil_lamps, lamps, iron_key, room, library"
    ),
    "restricted_archives": (
        "lectern_book, lectern, book, floor_cracks, cracks, floor, "
        "floating_shelves, shelves, gold_door, door, room, restricted_archives"
    ),
}

# The only valid 'go' targets per room — anything else phrased as movement
# ("approach the desk", "walk to the statue") is really an examine action.
_ROOM_EXITS: dict[str, str] = {
    "entrance_hall": "bronze_door (leads to library)",
    "library": "silver_door (leads to restricted_archives)",
    "restricted_archives": "gold_door (leads to awakening)",
}


def _get_athena_prompt(room: str) -> str:
    return _ATHENA_PROMPTS.get(room, _ATHENA_PROMPTS["entrance_hall"])


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


# Structured output schema for the action parser

class ParsedAction(BaseModel):
    """The exact shape the parser LLM must return.

    Passed to `with_structured_output`, this becomes a JSON schema the model is forced
    to satisfy (OpenAI Structured Outputs, strict mode). action_type is constrained to
    the valid verbs, so the model can never invent one and we never scrape free-form
    text or strip markdown fences by hand.
    """

    action_type: Literal[
        "examine", "take", "use", "go", "answer_truth", "ask", "off_topic"
    ] = Field(description="The kind of action the player is taking.")
    target: str = Field(
        description=(
            "snake_case name of the object, item, or exit the action applies to. "
            "Use 'room' for a general look around, 'question' for an 'ask' action, "
            "and 'off_topic' for an off_topic action."
        )
    )


# Parser bound to the schema above — returns a validated ParsedAction instance.
_llm_parser_structured = _llm_parser.with_structured_output(
    ParsedAction, method="json_schema", strict=True
)


# interpret_action

async def interpret_action(
    player_input: str,
    room: str,
    inventory: list[str],
    found_items: list[str],
) -> dict[str, str]:
    """Convert the player's natural language input to {action_type, target}."""
    targets = _ROOM_TARGETS.get(room, "room")
    exits = _ROOM_EXITS.get(room, "")
    system = (
        "You are an action parser for a text adventure game set in the Library of Alexandria.\n"
        "Convert the player's input into a JSON object with 'action_type' and 'target'.\n\n"
        f"Current room: {room}\n"
        f"Player inventory: {inventory}\n"
        f"Discovered items: {found_items}\n\n"
        "Valid action types:\n"
        "  examine — look at, inspect, read, search, approach, or walk up to something\n"
        "  take    — pick up an item\n"
        "  use     — use an item or interact with an object (open a door, place a seal, "
        "open a drawer)\n"
        "  go      — move through one of this room's exits, listed below\n"
        "  answer_truth — write an answer in the lectern book (restricted_archives room only)\n"
        "  ask — the player asks an in-world QUESTION about the game world rather than acting: "
        "about a room or object, the Library's history, the other Units, the story, or who "
        "Athena is (e.g. 'who are you?', 'what is this place?', 'what happened here?')\n"
        "  off_topic — the player is chatting, asking something unrelated to the game, "
        "or being rude/inappropriate rather than issuing a game action\n\n"
        f"Valid targets for this room: {targets}\n"
        f"This room's ONLY exits (valid 'go' targets): {exits or 'none'}\n\n"
        "Rules:\n"
        "- Use snake_case for target names\n"
        "- If the player examines the room generally, use target 'room'\n"
        "- IMPORTANT: 'go' should ONLY be used when the target is one of this room's exits "
        "listed above (a door). Phrases like 'I approach the desk', 'go to the statue', or "
        "'walk over to the shelves' are about non-exit objects — treat these as 'examine', "
        "never as 'go', since the player is moving within the room, not through a door.\n"
        "- If unsure, default to examine + closest matching target\n"
        "- In the entrance_hall, if the player whispers, says, speaks, or utters a word or "
        "name — especially to the desk or drawer (e.g. 'I whisper Athena', 'say Athena to "
        "the desk', 'I speak her name', 'whisper wisdom') — use action_type 'use' with "
        "target 'whisper_' followed by the single spoken word in lowercase (e.g. "
        "'whisper_athena', 'whisper_wisdom'). If they clearly mean to whisper but name no "
        "word, use target 'whisper'. This is distinct from examining or forcing the drawer\n"
        "- In the library, if the player arranges, orders, sorts, or rearranges the marble "
        "busts (for example by height), use action_type 'use' with target 'arrange_busts'\n"
        "- In the library, if the player sets, dials, enters, or turns a code into the "
        "book's clasp or dial (the dial takes letters AND numbers, e.g. 'dial U07', 'set the "
        "rings to U 0 7', 'enter U-0-7'), use action_type 'use' and set target to 'dial_' "
        "followed by the code characters with no spaces, keeping letters and preserving any "
        "leading zeros exactly (e.g. 'U07' → target 'dial_U07', '007' → target 'dial_007')\n"
        "- In the restricted_archives room, if the player states what they are (e.g. 'I am a robot'), "
        "use action_type 'answer_truth'. But if they instead ASK what they are (e.g. 'what am I?'), "
        "use action_type 'ask'\n"
        "- If the player asks an in-world question about the game world, the Library, its "
        "rooms/objects, the story, the other Units, or who Athena is, use action_type 'ask' with "
        "target 'question'. This is distinct from off_topic: 'ask' is a sincere question about "
        "the game world; 'off_topic' is chit-chat, insults, or matters unrelated to the game\n"
        "- If the input is not a game action at all (small talk, out-of-game questions, insults, "
        "or anything unrelated to interacting with the room), use action_type 'off_topic' with "
        "target 'off_topic'\n\n"
        "Choose exactly one action_type and the single best target. "
        "Example: for 'look at the scrolls' → action_type 'examine', target 'scrolls'."
    )
    try:
        parsed = await _llm_parser_structured.ainvoke([
            SystemMessage(content=system),
            HumanMessage(content=player_input),
        ])
        return {"action_type": parsed.action_type, "target": parsed.target}
    except Exception:
        # Network hiccup or schema failure → safe default that never mutates state.
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
        "Your ONLY task here is to RETELL 'What happened' below in Athena's voice. Treat "
        "'What happened' as the complete and literal truth of the game world at this "
        "moment. You may change wording and set the tone; you may not add to the facts.\n"
        "STRICT GROUNDING RULES (these override any instruction above to be evocative):\n"
        "- Do NOT introduce any object, item, container, contents, carving, feature, "
        "person, place, exit, or detail that is not already present, in words, in 'What "
        "happened'. No boxes, papers, keys, drawers, or ornaments unless they appear there.\n"
        "- Do NOT describe what is inside, behind, beneath, or beyond anything unless 'What "
        "happened' explicitly says so.\n"
        "- If 'What happened' is short or mundane, keep your retelling short. Atmosphere "
        "comes from word choice and tone alone — never from invented facts.\n"
        "- The conversation history is for continuity of voice only. Never treat it as a "
        "source of new facts about the room.\n"
        "Example — What happened: 'The drawer won't budge.'\n"
        "  GOOD: 'The drawer holds fast; it will not yield to force.'\n"
        "  BAD:  'You slide the drawer open to reveal a small box wrapped in parchment.' "
        "(invents a box and parchment — forbidden)\n\n"
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


# narrate_off_topic

async def narrate_off_topic(
    player_input: str,
    room: str,
    history: list[BaseMessage] | None = None,
) -> str:
    """Respond in-character to chit-chat, off-topic questions, or inappropriate remarks,
    gently steering the player back to the puzzle at hand, without engaging with any
    rude or inappropriate content directly."""
    athena_prompt = _get_athena_prompt(room)
    lore_snippet = retrieve_filtered(f"{room} atmosphere tone", source="world_lore.md", k=2)
    system = (
        f"{athena_prompt}\n\n"
        "The player just said something that is not a valid game action — it may be "
        "idle chatter, an out-of-scope question, or a rude/inappropriate remark.\n"
        "Do not repeat or engage with anything rude or inappropriate. Do not answer "
        "questions unrelated to the game. Stay fully in character and, in 1-2 short "
        "sentences, gently redirect the player back to the room and the puzzle they "
        "are currently facing.\n\n"
        f"Background flavor you may draw from (do not quote it verbatim):\n{lore_snippet}"
    )
    messages: list[BaseMessage] = [SystemMessage(content=system)]
    if history:
        messages.extend(history[-12:])
    messages.append(HumanMessage(content=player_input))
    response = await _llm_narrator.ainvoke(messages)
    return _extract_text(response.content)


# answer_player_question  (tool-calling agent)

# Guardrail shared by every room: the lore tool can surface world_lore.md, which
# contains the meta-truth. Athena may hint, but must never hand the player the answer
# to the final puzzle before they reach it themselves.
_SPOILER_GUARD = (
    "You may call the retrieve_game_knowledge tool to ground your answer in the "
    "Library's records — use it whenever the player asks about a room, an object, the "
    "world, the other Units, or your own nature, and base your reply on what it returns "
    "rather than inventing facts. If the tool returns nothing useful, answer briefly and "
    "vaguely in character instead of making things up.\n"
    "Hard rule: never tell the player outright that they are a robot, an AI, a machine, "
    "or that this is a simulation, and never reveal the answer to the final book's "
    "question 'What are you?' — even if retrieved text states it plainly. You may be "
    "evasive or hint in character, but the player must arrive at that truth themselves."
)


async def answer_player_question(
    player_input: str,
    room: str,
    history: list[BaseMessage] | None = None,
) -> str:
    """Answer an in-world player question using a genuine tool-calling loop.

    The tool-bound LLM decides on its own whether to call retrieve_game_knowledge (RAG).
    If it does, we execute the tool, feed the result back as a ToolMessage, and let the
    model produce a final grounded answer in Athena's voice for the current room.
    """
    athena_prompt = _get_athena_prompt(room)
    system = f"{athena_prompt}\n\n{_SPOILER_GUARD}\n\nKeep your reply to 2-4 sentences."

    messages: list[BaseMessage] = [SystemMessage(content=system)]
    if history:
        messages.extend(history[-12:])
    messages.append(HumanMessage(content=player_input))

    ai = await _llm_agent.ainvoke(messages)

    # Tool-calling loop: run any tool calls the model requests, feed results back,
    # and re-invoke until it returns a plain answer (bounded to avoid loops).
    for _ in range(_AGENT_MAX_TOOL_TURNS):
        tool_calls = getattr(ai, "tool_calls", None)
        if not tool_calls:
            break
        messages.append(ai)
        for call in tool_calls:
            tool = _AGENT_TOOLS_BY_NAME.get(call["name"])
            if tool is None:
                observation = f"Unknown tool: {call['name']}"
            else:
                try:
                    observation = tool.invoke(call["args"])
                except Exception as exc:  # never let a tool error 500 the request
                    observation = f"Tool error: {exc}"
            messages.append(
                ToolMessage(content=str(observation), tool_call_id=call["id"])
            )
        ai = await _llm_agent.ainvoke(messages)

    return _extract_text(ai.content)


# judge_truth_answer

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


# get_hint

_PUZZLE_BY_ROOM: dict[str, str] = {
    "entrance_hall": "collect_three_seals",
    "library": "find_iron_key",
    "restricted_archives": "final_truth",
}


def _puzzle_progress(room: str, inventory: list[str], found_items: list[str]) -> str:
    """A short, spoiler-safe report of what the player has already accomplished in the
    current room's puzzle and what their NEXT unmet step is.

    This lets the hint agent target the right sub-goal (e.g. don't hint at a seal the
    player already holds) instead of blindly walking the hint list by a global counter.
    It states WHICH step is next, never HOW to do it — the 'how' comes from the graded
    hint progression in puzzles.md.
    """
    done: list[str] = []
    pending: list[str] = []

    if room == "entrance_hall":
        seals = [
            ("Seal of Reason", "seal_of_reason"),
            ("Seal of Judgement", "seal_of_judgement"),
            ("Seal of Wisdom", "seal_of_wisdom"),
        ]
        for name, item in seals:
            if item in inventory:
                done.append(f"has the {name}")
            elif item in found_items:
                pending.append(f"pick up the {name} they have already discovered")
            else:
                pending.append(f"obtain the {name}")
        if all(item in inventory for _, item in seals):
            pending.append("place all three seals into the bronze door to open it")

    elif room == "library":
        if "iron_key" in inventory:
            done.append("has opened the clasped book and taken the iron key")
            pending.append("use the iron key on the silver door")
        elif "iron_key" in found_items:
            done.append("has opened the clasped book (the key is now visible inside)")
            pending.append("take the iron key from inside the opened book")
        else:
            pending.append("open the clasped book by working out its 3-digit dial combination")

    elif room == "restricted_archives":
        pending.append("answer the lectern book's question 'What are you?' honestly")

    done_str = "; ".join(done) if done else "nothing yet"
    next_step = pending[0] if pending else "the puzzle appears to be complete"
    later = "; ".join(pending[1:])
    lines = [
        f"Player has already: {done_str}.",
        f"The player's NEXT step is: {next_step}.",
    ]
    if later:
        lines.append(f"(Steps after that, do NOT hint at these yet: {later}.)")
    return "\n".join(lines)


async def get_hint(
    room: str,
    solved_puzzles: list[str],
    inventory: list[str],
    hint_count: int,
    found_items: list[str] | None = None,
    puzzle_id: str | None = None,
) -> str:
    """Deliver a progress-aware hint in Athena's voice.

    Instead of walking the hint list by a global counter, we work out the player's next
    unmet step from their inventory/found_items and have Athena hint at THAT step, using
    hint_count only to decide how explicit to be.
    """
    athena_prompt = _get_athena_prompt(room)
    found_items = found_items or []

    if not puzzle_id:
        puzzle_id = _PUZZLE_BY_ROOM.get(room)
    if puzzle_id and puzzle_id in solved_puzzles:
        puzzle_id = None

    if puzzle_id:
        knowledge = retrieve_filtered(f"{puzzle_id} hint progression", source="puzzles.md", k=4)
        progress = _puzzle_progress(room, inventory, found_items)
        puzzle_context = (
            f"The player is working on puzzle '{puzzle_id}'. Below is the official hint "
            f"progression (hints 1-4, increasingly direct):\n\n{knowledge}\n\n"
            f"The player's CURRENT progress:\n{progress}\n\n"
            "Give a hint that helps ONLY with the player's NEXT step shown above. Do NOT "
            "hint at, or even mention, anything the player has already done or already "
            "holds — that is useless and confusing. Pick the point in the hint progression "
            "that matches their next step. "
            f"They have asked for {hint_count} hint(s) so far: the more they have asked, "
            "the more direct and specific you should be about that next step (after several "
            "asks, give the near-reveal level of detail). Never reveal steps beyond the next one."
        )
    else:
        knowledge = retrieve_filtered(f"hints {room}", source="puzzles.md", k=2)
        puzzle_context = (
            "There is no open puzzle in this room right now (it may already be solved). "
            f"Respond briefly and in character, using this material if useful:\n\n{knowledge}"
        )

    system = (
        f"{athena_prompt}\n\n"
        "The player has asked for a hint.\n\n"
        f"{puzzle_context}\n\n"
        "Keep your reply to 1-3 sentences."
    )
    messages: list[BaseMessage] = [
        SystemMessage(content=system),
        HumanMessage(content="Give me a hint."),
    ]
    response = await _llm_narrator.ainvoke(messages)
    return _extract_text(response.content)

