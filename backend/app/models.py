import json
from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel


class GameSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    player_name: str
    current_room: str = "entrance_hall"
    inventory: str = Field(default="[]")       # JSON list of item IDs
    found_items: str = Field(default="[]")     # JSON list of discovered item IDs
    solved_puzzles: str = Field(default="[]")  # JSON list of solved puzzle IDs
    is_escaped: bool = False
    hint_count: int = 0
    memory: str = Field(default="[]")          # Agent conversation history (JSON)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def get_inventory(self) -> list[str]:
        return json.loads(self.inventory)

    def get_found_items(self) -> list[str]:
        return json.loads(self.found_items)

    def get_solved_puzzles(self) -> list[str]:
        return json.loads(self.solved_puzzles)

    def get_memory(self) -> list[dict]:
        return json.loads(self.memory)
