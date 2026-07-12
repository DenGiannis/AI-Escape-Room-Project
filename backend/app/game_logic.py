import json

from app.models import GameSession


# ---------- shared room descriptions (also used to narrate arrivals) ----------

_ROOM_DESCRIPTIONS: dict[str, str] = {
    "entrance_hall": (
        "You stand in the entrance hall of the Library of Alexandria. "
        "Marble columns rise to a vaulted ceiling painted with constellations. "
        "Shafts of golden sunlight fall across long tables covered in open scrolls. "
        "Rows of shelves line the walls. A marble statue of Athena stands near "
        "the entrance. A scholar's desk sits to one side. "
        "At the far end, a heavy bronze door bears the inscription: "
        "'Only those who carry the three seals of knowledge may pass.'"
    ),
    "library": (
        "You enter the Library. The shelves are taller here, "
        "the room darker, lit only by oil lamps. A row of three manuscripts is "
        "sealed in glass cases along one wall, and five small marble busts stand "
        "along a ledge. A reading desk holds a large open codex. One book on the "
        "back shelf sits apart from the rest, faintly trembling. It is bound shut "
        "by a bronze clasp set with a three-ring dial of engraved symbols, letters "
        "and numerals alike. A silver door at the far end has a single key slot."
    ),
    "restricted_archives": (
        "The Restricted Archives. The walls flicker. Marble columns phase in and "
        "out of existence at the edges of your vision. The floor is cracked. "
        "Through the cracks you can see scrolling code cascading into nothing. "
        "Several bookshelves float slightly above the floor. "
        "A grand lectern stands in the center, holding a single open book — "
        "the only perfectly stable object here. "
        "Behind the lectern, a plain unmarked golden door."
    ),
}


def _room_arrival_text(room: str) -> str:
    """Full description appended whenever the player enters a new room."""
    return _ROOM_DESCRIPTIONS.get(room, "")


# ---------- game state mutation helpers ----------

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

    # Entrance Hall

    if room == "entrance_hall":

        if action_type == "examine":

            if target in ("room", "area", "around", "surroundings", "entrance_hall", "hall"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": _ROOM_DESCRIPTIONS["entrance_hall"],
                }

            if target in ("scrolls", "shelves"):
                _add_found_item(game, "seal_of_reason")
                return {
                    "success": True,
                    "state_changes": {"found_item": "seal_of_reason"},
                    "raw_result": (
                        "Rows of scrolls line the wooden shelves, mostly catalogue entries. "
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
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A scholar's writing desk. Beneath a heavy inkwell lies a folded "
                        "papyrus note: 'The third seal is given, not taken. Lean close and "
                        "whisper the name of the goddess who watches over this hall."
                        "Say it, and the desk will open to you.' Beside the inkwell "
                        "is a small drawer."
                    ),
                }

            if target in ("drawer", "desk_drawer"):
                if "seal_of_wisdom" in game.get_found_items():
                    return {
                        "success": True,
                        "state_changes": {},
                        "verbatim": True,
                        "raw_result": (
                            "The drawer sits open. Inside, resting alone on the bare wood, "
                            "is a single clay tablet with an owl carved in relief. It's the "
                            "Seal of Wisdom. There is nothing else in the drawer."
                        ),
                    }
                return {
                    "success": False,
                    "state_changes": {},
                    "verbatim": True,
                    "raw_result": (
                        "The drawer won't budge. It doesn't seem to be locked, and yet it "
                        "doesn't yield to force either."
                    ),
                }

            if target in ("bronze_door", "door"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A heavy bronze door leads deeper into the Library. Above it, carved "
                        "in stone: 'Only those who carry the three seals of knowledge may pass.' "
                        "Three circular recesses wait to receive the seals."
                    ),
                }

            if target == "murals":
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Paintings cover the walls, scholars reading, copying manuscripts, "
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
                    "raw_result": "You take the Seal of Reason (a wax seal imprinted with a torch) from its scroll case.",
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
                    "raw_result": "You take the Seal of Judgement (a bronze medallion engraved with scales) from Athena's outstretched hand.",
                }

            if target == "seal_of_wisdom":
                if "seal_of_wisdom" in inventory:
                    return {"success": False, "state_changes": {}, "raw_result": "You already have the Seal of Wisdom."}
                if "seal_of_wisdom" not in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "The drawer hasn't given up its secret yet.",
                    }
                _add_to_inventory(game, "seal_of_wisdom")
                return {
                    "success": True,
                    "state_changes": {"add_item": "seal_of_wisdom"},
                    "raw_result": "You take the Seal of Wisdom (a clay tablet with an owl carved in relief) from the desk drawer.",
                }

        if action_type == "use":

            # Whisper the goddess's name (Athena) to the desk → the drawer opens.
            # The parser sends whispered words as 'whisper_<word>' (e.g. whisper_athena).
            is_whisper = target.startswith(("whisper", "say", "speak", "utter"))
            if ("athena" in target and (is_whisper or target == "athena")):
                if "seal_of_wisdom" in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "The drawer already stands open; the name has done its work.",
                    }
                _add_found_item(game, "seal_of_wisdom")
                return {
                    "success": True,
                    "state_changes": {"found_item": "seal_of_wisdom"},
                    "raw_result": (
                        "You lean close to the desk and breathe the name 'Athena.' "
                        "A soft click answers from within, and the small drawer slides open."
                    ),
                }
            if is_whisper:
                if "seal_of_wisdom" in game.get_found_items():
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": "The drawer already stands open.",
                    }
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": (
                        "You whisper to the desk, but nothing stirs. It seems to be waiting "
                        "for a particular name of the goddess who watches over this hall."
                    ),
                }

            if target in ("drawer", "desk_drawer") and "seal_of_wisdom" not in game.get_found_items():
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": (
                        "You pull and press at the drawer, but it refuses to move. Force "
                        "isn't the answer. Remember, the note beside it speaks of a whisper, not a pull."
                    ),
                }

        if action_type in ("use", "go"):
            if target in ("bronze_door", "door", "library"):
                seals = ["seal_of_reason", "seal_of_judgement", "seal_of_wisdom"]
                if all(s in inventory for s in seals):
                    game.inventory = json.dumps([i for i in inventory if i not in seals])
                    game.current_room = "library"
                    _solve_puzzle(game, "collect_three_seals")
                    return {
                        "success": True,
                        "state_changes": {"move_to": "library", "solve_puzzle": "collect_three_seals"},
                        "raw_result": (
                            "You press all three seals into the recesses. A deep resonant click "
                            "echoes through the hall and the bronze door swings open. "
                            "The Library's main area lies beyond.\n\n"
                            f"{_room_arrival_text('library')}"
                        ),
                    }
                found = game.get_found_items()
                missing_count = sum(1 for s in seals if s not in inventory)
                missing_known = [s.replace("_", " ") for s in seals if s not in inventory and s in found]
                detail = f" You know of but still need: {', '.join(missing_known)}." if missing_known else ""
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": (
                        f"The door has three empty recesses. You are still missing {missing_count} "
                        f"of the three seals.{detail}"
                    ),
                }

    # Library

    elif room == "library":

        found = game.get_found_items()
        book_open = "iron_key" in found  # the clasp only opens on the correct dial

        if action_type == "examine":

            if target in ("room", "area", "around", "surroundings", "library"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": _ROOM_DESCRIPTIONS["library"],
                }

            if target in ("vibrating_book", "book", "back_shelf", "clasp", "dial"):
                if book_open:
                    hollow = (
                        "the hollow cut through its pages now empty"
                        if "iron_key" in inventory
                        else "an iron key resting in a hollow cut through its pages"
                    )
                    return {
                        "success": True,
                        "state_changes": {},
                        "raw_result": (
                            f"The book lies open, its bronze clasp sprung, {hollow}."
                        ),
                    }
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A single book sits apart on the back shelf, faintly trembling. It is "
                        "bound shut by a bronze clasp set with a three-ring dial of engraved "
                        "symbols (letters and numerals alike) and it will not open by force; "
                        "clasped as it is, you cannot read a word inside. Two lines are engraved "
                        "around the clasp:\n"
                        "  'Where knowledge ends and error begins lies the way to my hidden knowledge.'\n"
                        "  'Three witnesses hold my number. Let the fewest speak first, the many speak last.'"
                    ),
                }

            if target in ("back_cover", "book_cover", "back_of_book"):
                if book_open:
                    if "iron_key" in inventory:
                        return {
                            "success": True,
                            "state_changes": {},
                            "raw_result": "The hollow cut through the pages is empty. You already took the key.",
                        }
                    return {
                        "success": True,
                        "state_changes": {},
                        "raw_result": "With the clasp open, an iron key sits in a hollow cut through the pages.",
                    }
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": (
                        "The book is clasped shut. You cannot reach its pages until the dial "
                        "is set to the right number."
                    ),
                }

            if target in ("glass_cases", "cases", "shelves"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Three sealed glass cases stand in a row. The first two are intact. "
                        "'On the Soul — Aristotle' and 'Elements — Euclid'. But "
                        "the last is broken: '[ERROR: REFERENCE NOT FOUND] — "
                        "[NULL]'. A null reference: a void where a book should be. What it "
                        "holds is nothing, only a zero."
                    ),
                }

            if target in ("marble_busts", "busts", "statues", "bust", "statue"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Five small marble busts of scholars stand in a jumbled row along a "
                        "ledge, each carved to a different height. Every base bears a broken "
                        "fragment of an etched mark, meaningless as they stand. They look as "
                        "though they are meant to be put in some order."
                    ),
                }

            if target in ("shifting_codex", "codex", "reading_desk", "desk"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "An open codex on the reading desk, its text crawling and unstable. One "
                        "line reads: 'The scholars maintained these records so that "
                        "[SIMULATION INTEGRITY: 94%] knowledge would never be lost,' and then "
                        "the page glitches: for a moment every character on it collapses into a "
                        "single repeated capital letter (U, U, U) cascading down the page "
                        "before the words swim back into place. Only that letter U lingers."
                    ),
                }

            if target in ("silver_door", "door"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A silver door at the far end of the stacks. A single slot for an "
                        "iron key is set into its face. Solid, heavy, immovable without the key."
                    ),
                }

            if target in ("oil_lamps", "lamps"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "Oil lamps burn steadily along the walls, throwing amber light across "
                        "the stacks. They are the room's only illumination, nothing more."
                    ),
                }

        if action_type == "use":

            # Arrange the five marble busts by height to reveal the third digit.
            if target in ("arrange_busts", "order_busts", "sort_busts", "busts",
                          "marble_busts", "statues"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "You lift the five busts and set them in order, shortest to tallest. "
                        "The broken fragments on their bases slide into line and resolve into "
                        "a single Greek numeral: seven."
                    ),
                }

            if target.startswith("dial") or target in ("clasp", "combination", "book_clasp"):
                code = (
                    "".join(ch for ch in target[4:] if ch.isalnum()).upper()
                    if target.startswith("dial")
                    else ""
                )
                if book_open:
                    return {
                        "success": True,
                        "state_changes": {},
                        "raw_result": "The clasp already hangs open.",
                    }
                if not code:
                    return {
                        "success": False,
                        "state_changes": {},
                        "raw_result": (
                            "The clasp has a three-ring dial of engraved symbols, letters and "
                            "numerals both. You will need to set three of them into it."
                        ),
                    }
                if code == "U07":
                    _add_found_item(game, "iron_key")
                    return {
                        "success": True,
                        "state_changes": {"found_item": "iron_key", "unlock": "vibrating_book"},
                        "raw_result": (
                            "You set the three rings, U, 0, 7. The clasp springs "
                            "open with a soft click and the book falls open. Cut through the "
                            "thickness of its pages is a hollow, and inside it rests an iron key."
                        ),
                    }
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": (
                        f"You set the rings to {'-'.join(code)} and pull, but nothing gives; "
                        "the dial slips back to its starting position. That is not the number."
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
                        "raw_result": "You haven't found a key yet. The book on the back shelf is still clasped shut.",
                    }
                _add_to_inventory(game, "iron_key")
                return {
                    "success": True,
                    "state_changes": {"add_item": "iron_key"},
                    "raw_result": "You take the iron key. It is cold to the touch.",
                }

        if action_type in ("use", "go"):
            if target in ("silver_door", "door", "restricted_archives"):
                if "iron_key" in inventory:
                    # The key is spent opening the door — consume it, as the bronze
                    # door consumes its seals.
                    game.inventory = json.dumps([i for i in inventory if i != "iron_key"])
                    game.current_room = "restricted_archives"
                    _solve_puzzle(game, "find_iron_key")
                    return {
                        "success": True,
                        "state_changes": {
                            "remove_item": "iron_key",
                            "move_to": "restricted_archives",
                            "solve_puzzle": "find_iron_key",
                        },
                        "raw_result": (
                            "You insert the iron key into the slot. The silver door grinds open. "
                            "The air that escapes carries no smell at all.\n\n"
                            f"{_room_arrival_text('restricted_archives')}"
                        ),
                    }
                return {
                    "success": False,
                    "state_changes": {},
                    "raw_result": "The silver door has a slot for a key. You don't have one.",
                }

    # Restricted Archives

    elif room == "restricted_archives":

        if action_type == "examine":

            if target in ("room", "area", "around", "surroundings", "restricted_archives", "archives"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": _ROOM_DESCRIPTIONS["restricted_archives"],
                }

            if target in ("lectern_book", "lectern", "book"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A plain open book on the grand lectern, the only perfectly stable "
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
                        "through states as you watch, ancient Greek texts, corrupted data "
                        "entries, system logs, blank pages, then back to ancient texts again. "
                        "You cannot hold any of them."
                    ),
                }

            if target in ("gold_door", "door"):
                return {
                    "success": True,
                    "state_changes": {},
                    "raw_result": (
                        "A plain, unmarked golden door stands behind the lectern. No lock, no "
                        "keyhole, no handle you can force. Somehow you know the book holds the "
                        "answer to opening it."
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
                        "Then the golden door swings open on its own. "
                        "Light, clean and sourceless, pours through. "
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

    # Fallback

    return {
        "success": False,
        "state_changes": {},
        "raw_result": f"You cannot {action_type} {target.replace('_', ' ')} here.",
    }