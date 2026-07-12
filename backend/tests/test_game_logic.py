from app.game_logic import process_action
from app.models import GameSession


def new_game() -> GameSession:
    return GameSession(player_name="Tester")


# Entrance Hall

def test_fresh_game_starts_in_entrance_hall():
    game = new_game()
    assert game.current_room == "entrance_hall"
    assert game.get_inventory() == []
    assert game.get_solved_puzzles() == []
    assert game.is_escaped is False


def test_cannot_take_seal_before_finding_it():
    game = new_game()
    result = process_action(game, "take", "seal_of_reason")
    assert result["success"] is False
    assert "seal_of_reason" not in game.get_inventory()


def test_examine_reveals_seal_then_it_can_be_taken():
    game = new_game()
    process_action(game, "examine", "scrolls")
    assert "seal_of_reason" in game.get_found_items()
    result = process_action(game, "take", "seal_of_reason")
    assert result["success"] is True
    assert "seal_of_reason" in game.get_inventory()


def test_drawer_is_locked_until_the_name_is_whispered():
    game = new_game()
    locked = process_action(game, "examine", "drawer")
    assert locked["success"] is False
    process_action(game, "use", "whisper_athena")
    assert "seal_of_wisdom" in game.get_found_items()


def test_bronze_door_requires_all_three_seals():
    game = new_game()
    blocked = process_action(game, "use", "bronze_door")
    assert blocked["success"] is False
    assert game.current_room == "entrance_hall"


def solve_entrance_hall(game: GameSession) -> None:
    """Collect all three seals and open the bronze door -> moves to library."""
    process_action(game, "examine", "scrolls")
    process_action(game, "take", "seal_of_reason")
    process_action(game, "examine", "marble_statue")
    process_action(game, "take", "seal_of_judgement")
    process_action(game, "use", "whisper_athena")
    process_action(game, "take", "seal_of_wisdom")
    process_action(game, "use", "bronze_door")


def test_full_entrance_hall_solve_moves_to_library():
    game = new_game()
    solve_entrance_hall(game)
    assert game.current_room == "library"
    assert "collect_three_seals" in game.get_solved_puzzles()
    assert game.get_inventory() == []


# Library

def test_wrong_dial_code_does_not_open_the_book():
    game = new_game()
    solve_entrance_hall(game)
    result = process_action(game, "use", "dial_123")
    assert result["success"] is False
    assert "iron_key" not in game.get_found_items()


def test_correct_dial_code_reveals_the_iron_key():
    game = new_game()
    solve_entrance_hall(game)
    result = process_action(game, "use", "dial_U07")
    assert result["success"] is True
    assert "iron_key" in game.get_found_items()


def solve_library(game: GameSession) -> None:
    """Open the clasped book, take the key, unlock the silver door."""
    process_action(game, "use", "dial_U07")
    process_action(game, "take", "iron_key")
    process_action(game, "use", "silver_door")


def test_full_library_solve_moves_to_restricted_archives():
    game = new_game()
    solve_entrance_hall(game)
    solve_library(game)
    assert game.current_room == "restricted_archives"
    assert "find_iron_key" in game.get_solved_puzzles()
    assert "iron_key" not in game.get_inventory()


# Restricted Archives (the ending)

def test_dishonest_final_answer_does_not_escape():
    game = new_game()
    solve_entrance_hall(game)
    solve_library(game)

    result = process_action(game, "answer_truth", "false")
    assert result["success"] is False
    assert game.is_escaped is False


def test_honest_final_answer_escapes():
    game = new_game()
    solve_entrance_hall(game)
    solve_library(game)
    result = process_action(game, "answer_truth", "true")
    assert result["success"] is True
    assert game.is_escaped is True
    assert game.current_room == "awakening"
    assert "final_truth" in game.get_solved_puzzles()


# Fallback

def test_unknown_action_fails_gracefully():
    game = new_game()
    result = process_action(game, "examine", "spaceship")
    assert result["success"] is False
    assert "raw_result" in result  # still returns a well-formed response
