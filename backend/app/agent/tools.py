import json

from langchain_core.tools import tool

from app.agent.rag import retrieve


@tool
def retrieve_game_knowledge(query: str) -> str:
    """Retrieve room descriptions, item info, puzzle hints, and lore from the game knowledge base."""
    if not query or not query.strip():
        return json.dumps({"error": "No query provided"}, ensure_ascii=False)
    try:
        result = retrieve(query)
        return result
    except Exception as exc:
        return json.dumps(
            {"error": "Knowledge retrieval failed", "details": str(exc)},
            ensure_ascii=False,
        )
