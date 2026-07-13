# How the AI Escape Room Works (A Walkthrough)

This document explains the whole project in plain language: what each file does,
how the pieces talk to each other, and how the "AI parts" (agents, tools, RAG)
actually work and when they run.

The mental model to keep in your head:

> **The game rules are deterministic. The AI is a layer wrapped around
> them.** The AI turns the inputs into a command, and turns the game's plain
> response back into atmospheric story text. The AI never decides what is true
> in the escape room game. The game logic does.

---

## 1. Diagram

```
   CLIENT - Player (browser)
      │  type: "look at the statue"
      ▼
┌─────────────────────┐        HTTP (JSON)
│  frontend/app.py    │  ───────────────────────►  ┌──────────────────────────┐
│  (Streamlit UI)     │                            │  backend (FastAPI)       │
│  - draws the chat   │  ◄───────────────────────  │  - runs the game + AI    │
│  - shows inventory  │        JSON response       └──────────────────────────┘
└─────────────────────┘
```

There are two programs running at the same time:

1. **The frontend** (`frontend/app.py`) — a Streamlit web app. It only draws the
   screen and sends what you type to the backend. It contains **zero** game logic.
2. **The backend** (everything in `backend/`) — a FastAPI server. It holds the
   game rules, the database, and all the AI calls.

---

## 2. What each file does

### Frontend

| File | What it does |
|------|--------------|
| `frontend/app.py` | The entire UI. Draws the start screen, the chat, the sidebar (inventory, hints), and the ending. When you type something, it POSTs to the backend and prints the reply. Talks to the backend with the `httpx` HTTP library. |
| `frontend/assets/` | Images (room pictures, title screen). These are optional and the app runs fine without them. |

### Backend

| File | What it does |
|------|--------------|
| `backend/app/main.py` | **Start here.** Creates the FastAPI `app`, turns on CORS, creates the database tables on startup (`init_db`), and plugs in all the routes. |
| `backend/app/api/main.py` | Collects the game endpoints into one `api_router`. |
| `backend/app/api/routes/game.py` | **The heart of the request handling.** Defines every URL the frontend can call (`/start`, `/action`, `/hint`, `/inventory`, `/summary`) and orchestrates what happens for each one. |
| `backend/app/api/deps.py` | Provides a database session to any endpoint that asks for one (`SessionDep`). "deps" = dependencies. |
| `backend/app/core/db.py` | Sets up the database connection (SQLite) and the `get_session` helper. |
| `backend/app/core/config.py` | App settings: the OpenAI API key, which model to use, the DB location. Loaded from a `.env` file. |
| `backend/app/models.py` | Defines the **one** database table, `GameSession`. A saved game: which room you're in, your inventory, solved puzzles, conversation memory, etc. |

### Backend — AI Part

| File | What it does |
|------|--------------|
| `backend/app/game_logic.py` | **The deterministic game engine.** One big function, `process_action(game, action_type, target)`. Given a normalized command like `("examine", "statue")`, it decides what happens, changes the saved game (adds an item, opens a door, moves rooms), and returns a plain-text result. **No AI here at all**! Only `if` statements. This is the "source of truth." |
| `backend/app/agent/graph.py` | **All the AI lives here.** Every function that talks to the LLM: understanding your input, writing Athena's replies, answering questions, judging the final answer, giving hints. Also the memory helpers. |
| `backend/app/agent/rag.py` | The **RAG** system: loads the knowledge documents, turns them into a searchable vector store, and provides search functions. |
| `backend/app/agent/tools.py` | Defines the **tool** the agent can call (`retrieve_game_knowledge`), which is just a wrapper around RAG search. |
| `backend/app/data/*.md` | The **knowledge base**. Plain Markdown files describing the world, rooms, items, puzzles, and Athena's character. This is the files that RAG searches through. |

---

## 3. The flow of one action

Let's trace exactly what happens when you type **"look at the statue"** and hit enter during gameplay.

```
frontend/app.py
   │  POST /api/v1/game/action  { session_id, input: "look at the statue" }
   ▼
game.py -> game_action()   ◄── this function coordinates everything below
   │
   │  STEP 1 — Understand the input (eg. English language)
   ▼
graph.py -> interpret_action()        [LLM call #1 — structured output]
   │      returns: { action_type: "examine", target: "marble_statue" }
   │
   │  STEP 2 — Decide which path this is
   │      (examine/take/use/go -> normal | off_topic | ask | answer_truth)
   │      "examine" -> normal path
   ▼
game_logic.py -> process_action(game, "examine", "marble_statue")   [NO AI]
   │      - marks the Seal of Judgement as "found"
   │      - returns plain text: "A marble statue of Athena stands near..."
   │
   │  STEP 3 — Make it sound like Athena
   ▼
graph.py -> narrate_result(raw_text, ...)     [LLM call #2 — prompt engineering]
   │      rewrites the plain text in Athena's voice for the current room
   │
   │  STEP 4 — Save + reply
   ▼
game.py: save conversation to memory, commit to DB, return JSON
   │
   ▼
frontend/app.py: prints Athena's reply in the chat
```

**Key takeaway:** there are usually **two** LLM calls per action — one to *read* your
input (turn English -> command) and one to *write* the reply (turn the game's plain
result -> Athena's voice). The actual game decision in the middle is just Python.

### Why split it this way?

- **Reading** (`interpret_action`) uses a strict, temperature-0 model so it reliably
  produces a clean command and never "hallucinates" a new game rule.
- **The rules** (`process_action`) are plain code, so the game can never be tricked
  into giving you an item you didn't earn. The AI can't override the truth.
- **Writing** (`narrate_result`) uses a slightly creative model to make it atmospheric,
  but with strict instructions to only restate the facts it was given.

---

## 4. The different "paths" an action can follow

After `interpret_action` labels your input, `game_action` in `game.py` routes it to
one of four handlers:

| `action_type` | Meaning | Who handles it | Touches game state? |
|---------------|---------|----------------|---------------------|
| `examine` / `take` / `use` / `go` | A real game move | `process_action` -> `narrate_result` | **Yes** |
| `off_topic` | Chit-chat, insults, unrelated | `narrate_off_topic` | No |
| `ask` | An in-world question ("who are you?") | `answer_player_question` (**the agent**) | No |
| `answer_truth` | Answering the final book's question | `judge_truth_answer` -> `process_action` | **Yes** |

Only real moves and the final answer can change the status of the current saved game. Questions and
chatter are "read-only", which basically means that they reply without altering the state.

---

## 5. How the AGENT works, and when it runs

**Where:** `answer_player_question()` in `graph.py`.
**When:** only when you *ask a question about the world/lore* (`action_type == "ask"`),
e.g. "Who are you?", "What is this place?"

An **agent** (as opposed to a simple LLM call) is an LLM that can 
**decide to use tools on its own**. Here's the loop in simple terms:

```
1. We give the LLM your question + the list of tools it's allowed to use.
2. The LLM thinks. It can either:
      (a) answer directly, OR
      (b) say "I want to call retrieve_game_knowledge('who is Athena')"
3. If it asked for a tool, then run that tool and hand the result back to it.
4. The LLM reads the tool result and tries again (back to step 2).
5. This repeats up to 3 times, then it must give a final answer.
```

No one decides when to search the knowledge base except of the LLM. 
That's what makes it an "agent" and not just a prompt. In `graph.py` this
loop is the `for _ in range(_AGENT_MAX_TOOL_TURNS)` block.

The agent is created near the top of `graph.py` with:

```python
_llm_agent = ChatOpenAI(...).bind_tools(_AGENT_TOOLS)
```

`bind_tools` is what tells the LLM "these tools exist and here's how to ask for them."

---

## 6. How the TOOL works, and when it's called

**Where:** `retrieve_game_knowledge()` in `tools.py`.
**When:** whenever the agent (above) decides it needs background facts to answer you.

```python
@tool
def retrieve_game_knowledge(query: str) -> str:
    """Search the Library's records for grounded background knowledge...
    Does NOT contain puzzle solutions."""
    return retrieve_player_safe(query)   # <- this is a RAG search
```

So the chain is: agent decides -> calls the tool -> the tool runs a RAG search ->
returns text -> agent uses that text to write its answer. The tool is deliberately
wired to the "player-safe" RAG search so it can never leak puzzle answers. It will
never search the puzzle.md file for answers!!

---

## 7. RAG

**Where:** `rag.py`, using the `.md` files in `data/`.

### The one-time setup (building the searchable index)

```
data/*.md                                          (world_lore, rooms, items, puzzles, athena)
   │  read the files
   ▼
MarkdownTextSplitter                               split each file into ~500-char "chunks"
   │
   ▼
OpenAIEmbeddings                                   turn each chunk into a vector (list of numbers
   │                                               that captures its meaning)
   ▼
FAISS vector store                                 an index you can search by meaning, not keywords
```

This happens once and is cached (`@lru_cache`), so it's not rebuilt on every request.

### The search (happens on each question/hint)

When we search with a query like `"who is Athena"`, FAISS finds the chunks whose
**meaning** is closest to the query (this is "similarity search") and returns them as
text. That text gets pasted into the LLM's prompt.

### Two ways of search
| Function in `rag.py` | Used by | Special behaviour |
|----------------------|---------|-------------------|
| `retrieve_player_safe()` | The **tool** / agent (player-facing answers) | **Excludes `puzzles.md`** so solutions can never leak to the player. |
| `retrieve_filtered()` | **Hints** and off-topic flavour | Searches **one specific file** (e.g. only `puzzles.md` for hints). |

Basically hints are *allowed* to read the puzzle solutions file. On the other hand 
player Q&A is *not*. Same RAG engine, different ways to search.

---

## 8. Where else the AI is used

Besides the agent, `graph.py` has a few more LLM-powered functions.
These are single, focused LLM calls:

| Function | Job | Technique |
|----------|-----|-----------|
| `interpret_action` | Input -> `{action_type, target}` | **Structured Output** (the model is forced to return a fixed JSON shape via `ParsedAction`) |
| `narrate_result` | Plain game result -> Athena's voice | **Prompt Engineering** (persona + strict "don't invent facts" rules) |
| `narrate_off_topic` | Politely redirect out of topic chat inputs | Prompt Engineering + RAG |
| `judge_truth_answer` | Is the final answer correct? -> `True`/`False` | LLM-as-a-judge |
| `get_hint` | A progress-aware hint | RAG (reads `puzzles.md`) + Prompt Engineering |

---

## 9. Memory & saved state

Everything about your game lives in **one row** of the `GameSession` table
(`models.py`). Notably:

- `current_room`, `inventory`, `found_items`, `solved_puzzles`, `is_escaped` — your progress.
- `memory` — the recent back-and-forth conversation, stored as JSON. This is what lets
  Athena stay consistent across messages.

On every action, `game.py`:
1. loads palyer's row from the DB,
2. runs the steps from Section 3,
3. appends the new exchange to `memory` (keeping only the last ~40 messages),
4. commits the row back to the DB.

---

## 10. End-to-end examples

**Example A — a normal move: "open the drawer" (before the whisper puzzle is solved)**
1. `interpret_action` -> `{use, drawer}`
2. normal path -> `process_action` -> returns *"The drawer won't budge..."* (state unchanged)
3. `narrate_result` -> Athena says it more poetically
4. saved & returned

**Example B — a question: "Athena, who are you really?"**
1. `interpret_action` -> `{ask, question}`
2. `ask` path -> `answer_player_question` (**Agent**)
3. the agent decides to call `retrieve_game_knowledge("who is Athena")` (**Tool call**)
4. the tool runs `retrieve_player_safe` (**RAG**, skips (spoilers) `puzzles.md`)
5. the agent reads the returned lore and answers in character, while a hard rule in
   its prompt stops it from revealing the twist ending
6. game state is untouched but the reply is saved to memory

---