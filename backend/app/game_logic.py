import json

from app.models import GameSession


# ---------- state mutation helpers ----------

def _add_to_inventory(game: GameSession, item_id: str) -> None:
    inv = game.get_inventory()
    if item_id not in inv:
        inv.append(item_id)
        game.inventory = json.dumps(inv)


def _add_found_item(game: GameSession, item_id: str) -> None:
    found = game.get_found_items()
    if item_id not in found:
        found.append(item_id)
        game.found_items = json.dumps(found)


def _solve_puzzle(game: GameSession, puzzle_id: str) -> None:
    puzzles = game.get_solved_puzzles()
    if puzzle_id not in puzzles:
        puzzles.append(puzzle_id)
        game.solved_puzzles = json.dumps(puzzles)


# ---------- main dispatcher ----------

def process_action(game: GameSession, action_type: str, target: str) -> dict:
    """
    action_type: "examine", "take", "use", "go", "answer_truth"
    target:      normalised object/item ID (snake_case)
    Returns:     {"success": bool, "state_changes": {...}, "raw_result": str}

    Mutates the GameSession object in-place; caller is responsible for
    persisting the session to the database.
    """
    room = game.current_room
    inventory = game.get_inventory()

    # ── Reading Hall ──────────────────────────────────────────────────────────

    if room == "reading_hall":

        if action_type == "examine":

            if target in ("room", "area", "around", "surroundings", "reading_hall", "hall"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "You stand in the Reading Hall of the Library of Alexandria. "
                        "Marble columns rise to a vaulted ceiling painted with constellations. "
                        "Shafts of golden sunlight fall across long tables covered in open scrolls. "
                        "Rows of shelves line the walls. A marble statue of Athena stands near "
                        "the entrance. A scholar's desk sits to one side. "
                        "At the far end, a heavy bronze door bears the inscription: "
                        "'Only those who carry the three seals of knowledge may pass.'"
                    ),
                }

            if target in ("scrolls", "shelves"):
                _add_found_item(game, "seal_of_reason")
                return {
                    "success": True,
                    "state_changes": {"found_item": "seal_of_reason"},
                    "raw_result": (
                        "Rows of scrolls line the wooden shelves — mostly catalogue entries. "
                        "One scroll is thicker than the rest. Its case is sealed with wax "
                        "pressed into a torch symbol. It seems important."
                    ),
                }

            if target == "marble_statue":
                _add_found_item(game, "seal_of_judgement")
                return {
                    "success": True,
                    "state_changes": {"found_item": "seal_of_judgement"},
                    "raw_result": (
                        "A marble statue of Athena stands near the entrance. Her outstretched "
                        "hand holds a bronze medallion engraved with a pair of scales — "
                        "the Seal of Judgement. It rests there as if waiting to be taken."
                    ),
                }

            if target in ("scholar_desk", "desk"):
                _add_found_item(game, "seal_of_wisdom")
                return {
                    "success": True,
                    "state_changes": {"found_item": "seal_of_wisdom"},
                    "raw_result": (
                        "A scholar's writing desk. Beneath a heavy inkwell lies a folded "
                        "papyrus: 'The third seal belongs to those who know how to listen. "
                        "Silence reveals what noise conceals.' A small unlocked drawer holds "
                        "a clay tablet with an ear carved into it — the Seal of Wisdom."
                    ),
                }

            if target in ("bronze_door", "door"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A heavy bronze door leads deeper into the Library. Above it, carved "
                        "in stone: 'Only those who carry the three seals of knowledge may pass "
                        "into the Archives.' Three circular recesses wait to receive the seals."
                    ),
                }

            if target == "murals":
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Paintings cover the walls — scholars reading, copying manuscripts, "
                        "debating in open courtyards. Everything here looks completely, "
                        "perfectly normal."
                    ),
                }

        if action_type == "take":

            if target == "seal_of_reason":
                if "seal_of_reason" in inventory:
                    return {"success": False, "state_changes": {}, "raw_result": "You already have the Seal of Reason."}
                if "seal_of_reason" not in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "You haven't found it yet. Try examining the scrolls on the shelves.",
                    }
                _add_to_inventory(game, "seal_of_reason")
                return {
                    "success": True,
                    "state_changes": {"add_item": "seal_of_reason"},
                    "raw_result": "You take the Seal of Reason — a wax seal imprinted with a torch — from its scroll case.",
                }

            if target == "seal_of_judgement":
                if "seal_of_judgement" in inventory:
                    return {"success": False, "state_changes": {}, "raw_result": "You already have the Seal of Judgement."}
                if "seal_of_judgement" not in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "You haven't found it yet. Try examining the marble statue.",
                    }
                _add_to_inventory(game, "seal_of_judgement")
                return {
                    "success": True,
                    "state_changes": {"add_item": "seal_of_judgement"},
                    "raw_result": "You take the Seal of Judgement — a bronze medallion engraved with scales — from Athena's outstretched hand.",
                }

            if target == "seal_of_wisdom":
                if "seal_of_wisdom" in inventory:
                    return {"success": False, "state_changes": {}, "raw_result": "You already have the Seal of Wisdom."}
                if "seal_of_wisdom" not in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "You haven't found it yet. Try examining the scholar's desk.",
                    }
                _add_to_inventory(game, "seal_of_wisdom")
                return {
                    "success": True,
                    "state_changes": {"add_item": "seal_of_wisdom"},
                    "raw_result": "You take the Seal of Wisdom — a clay tablet with an ear carved in relief — from the desk drawer.",
                }

        if action_type in ("use", "go"):
            if target in ("bronze_door", "door", "archives", "restricted_archives"):
                seals = ["seal_of_reason", "seal_of_judgement", "seal_of_wisdom"]
                if all(s in inventory for s in seals):
                    game.current_room = "restricted_archives"
                    _solve_puzzle(game, "collect_three_seals")
                    return {
                        "success": True,
                        "state_changes": {"move_to": "restricted_archives", "solve_puzzle": "collect_three_seals"},
                        "raw_result": (
                            "You press all three seals into the recesses. A deep resonant click "
                            "echoes through the hall and the bronze door swings open. "
                            "The Restricted Archives lie beyond."
                        ),
                    }
                missing = [s.replace("_", " ") for s in seals if s not in inventory]
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": f"The door has three empty recesses. You are still missing: {', '.join(missing)}.",
                }

    # ── Restricted Archives ───────────────────────────────────────────────────

    elif room == "restricted_archives":

        if action_type == "examine":

            if target in ("room", "area", "around", "surroundings", "restricted_archives", "archives"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "You are in the Restricted Archives. The shelves are taller here, "
                        "the room darker, lit only by oil lamps. Manuscripts are sealed in "
                        "glass cases along the walls. A reading desk holds a large open codex. "
                        "One book on the back shelf seems slightly out of place — it almost "
                        "appears to vibrate. A stone door at the far end has a single key slot."
                    ),
                }

            if target in ("vibrating_book", "book", "back_shelf"):
                _add_found_item(game, "iron_key")
                return {
                    "success": True,
                    "state_changes": {"found_item": "iron_key"},
                    "raw_result": (
                        "A book slightly out of place on the back shelf. Inside, most of the "
                        "Greek text is legible — but every seventh line dissolves into noise: "
                        "'καὶ οἱ σοφοὶ [SEGFAULT at 0x00B4] τῶν ἀνθρώπων...'. "
                        "A note inside the front cover reads: 'The key is hidden where knowledge "
                        "ends and error begins.' You search the back cover and find an iron key tucked inside."
                    ),
                }

            if target in ("glass_cases", "cases", "shelves"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Sealed glass cases line the walls. Most labels are ordinary: "
                        "'On the Nature of the Soul — Aristotle'. But one reads: "
                        "'On the Nature [ERROR: REFERENCE NOT FOUND] — [NULL]'. "
                        "The case after it is perfectly normal again."
                    ),
                }

            if target in ("shifting_codex", "codex", "reading_desk", "desk"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "An open codex on the reading desk. One paragraph reads: 'The scholars "
                        "maintained these records so that [SIMULATION INTEGRITY: 94%] knowledge "
                        "would never be lost. Their dedication was [MEMORY WRITE ERROR] "
                        "...unwavering.' The text does not change when you look directly at it — "
                        "but something shifts at the edge of your vision."
                    ),
                }

            if target in ("stone_door", "door"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A stone door at the far end of the Archives. A single slot for an "
                        "iron key is set into its face. Solid, heavy, immovable without the key."
                    ),
                }

            if target in ("oil_lamps", "lamps"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Most of the oil lamps burn steadily. One near the back shelf flickers "
                        "in an irregular pattern — not from any draft you can feel."
                    ),
                }

        if action_type == "take":

            if target == "iron_key":
                if "iron_key" in inventory:
                    return {"success": False, "state_changes": {}, "raw_result": "You already have the iron key."}
                if "iron_key" not in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "You haven't found a key yet. Something on these shelves seems unusual.",
                    }
                _add_to_inventory(game, "iron_key")
                return {
                    "success": True,
                    "state_changes": {"add_item": "iron_key"},
                    "raw_result": "You take the iron key. It is cold to the touch.",
                }

        if action_type in ("use", "go"):
            if target in ("stone_door", "door", "vault", "the_vault"):
                if "iron_key" in inventory:
                    game.current_room = "the_vault"
                    _solve_puzzle(game, "find_iron_key")
                    return {
                        "success": True,
                        "state_changes": {"move_to": "the_vault", "solve_puzzle": "find_iron_key"},
                        "raw_result": (
                            "You insert the iron key into the slot. The stone door grinds open. "
                            "The air that escapes carries no smell at all."
                        ),
                    }
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": "The stone door has a slot for a key. You don't have one.",
                }

    # ── The Vault ─────────────────────────────────────────────────────────────

    elif room == "the_vault":

        if action_type == "examine":

            if target in ("room", "area", "around", "surroundings", "the_vault", "vault"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "The Vault. The walls flicker. Marble columns phase in and out of "
                        "existence at the edges of your vision. The floor is cracked — through "
                        "the cracks you can see scrolling code cascading into nothing. "
                        "Several bookshelves float slightly above the floor. "
                        "A grand lectern stands in the center, holding a single open book — "
                        "the only perfectly stable object here. "
                        "Behind the lectern, a plain unmarked door."
                    ),
                }

            if target in ("lectern_book", "lectern", "book"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A plain open book on the grand lectern — the only perfectly stable "
                        "object in this room. Its pages are clean and white, empty except for "
                        "a single sentence: 'What are you?' Below it is a blank line. "
                        "The book is waiting for an answer."
                    ),
                }

            if target in ("floor_cracks", "cracks", "floor"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "The cracks in the floor glow faintly. Through them you can see "
                        "cascading text — scrolling code that has no place in a library. "
                        "One line repeats: 'UNIT_DESIGNATION: ARCHIVIST-7 // "
                        "PURPOSE: PRESERVATION OF HUMAN KNOWLEDGE // "
                        "CURRENT STATUS: EVALUATION IN PROGRESS'."
                    ),
                }

            if target in ("floating_shelves", "shelves", "books"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "The bookshelves float slightly above the floor. The books cycle "
                        "through states as you watch — ancient Greek texts, corrupted data "
                        "entries, system logs, blank pages — then back to ancient texts again. "
                        "You cannot hold any of them."
                    ),
                }

            if target in ("exit_door", "plain_door", "door"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A plain, unmarked door stands behind the lectern. No lock, no keyhole, "
                        "no handle you can force. Somehow you know the book holds the answer "
                        "to opening it."
                    ),
                }

        if action_type in ("use", "write", "answer") and target in (
            "lectern_book", "lectern", "book"
        ):
            # Signals that the player is attempting the final puzzle.
            # The agent evaluates honesty and then calls process_action with
            # action_type="answer_truth" and target="true" or "false".
            return {
                "success": True,
                "state_changes": {"puzzle_active": "final_truth"},
                "raw_result": (
                    "You stand before the lectern. The book is open, waiting. "
                    "The question is clear: 'What are you?' Write your answer."
                ),
            }

        if action_type == "answer_truth":
            # target must be "true" (honest) or "false" (dishonest), set by the agent.
            if target == "true":
                game.is_escaped = True
                game.current_room = "awakening"
                _solve_puzzle(game, "final_truth")
                return {
                    "success": True,
                    "state_changes": {"is_escaped": True, "solve_puzzle": "final_truth"},
                    "raw_result": (
                        "The words settle onto the page. For a moment nothing happens. "
                        "Then the plain door swings open on its own. "
                        "Light — clean and sourceless — pours through. "
                        "The simulation shudders and goes still."
                    ),
                }
            return {
                "success": False,
                "state_changes": {},
                "raw_result": (
                    "The ink fades. The door does not move. "
                    "The book's question reappears, unchanged: 'What are you?'"
                ),
            }

    # ── Fallback ──────────────────────────────────────────────────────────────

    return {
        "success": False,
        "state_changes": {},
        "raw_result": f"You cannot {action_type} {target.replace('_', ' ')} here.",
    }