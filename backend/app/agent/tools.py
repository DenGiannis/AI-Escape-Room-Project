import json

from langchain_core.tools import tool

from app.agent.rag import retrieve_player_safe


@tool
def retrieve_game_knowledge(query: str) -> str:
    """Search the Library's records for grounded background knowledge.

    Call this to answer a player's in-world question: about a room, an object, the
    world and its history, the other Units, or who Athena is, using real detail from
    the knowledge base instead of guessing. Pass a short natural-language `query`
    describing what you need (e.g. "who is Athena", "history of the library",
    "the marble busts"). Returns relevant excerpts as text. Does NOT contain puzzle
    solutions, combinations, or hint answers.
    """
    if not query or not query.strip():
        return json.dumps({"error": "No query provided"}, ensure_ascii=False)
    try:
        return retrieve_player_safe(query)
    except Exception as exc:
        return json.dumps(
            {"error": "Knowledge retrieval failed", "details": str(exc)},
            ensure_ascii=False,
        )
