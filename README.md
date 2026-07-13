# AI Escape Room — Project Archivist

> A GenAI-powered text adventure. You awaken trapped in the Library of Alexandria and
> must solve three rooms of puzzles to escape.

## Installation

```bash
# 1. Clone
git clone https://github.com/DenGiannis/AI-Escape-Room-Project.git
cd AI-Escape-Room-Project

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

Copy the example env file and add your own OpenAI key:

```bash
cp .env.example .env   # Windows: copy .env.example .env
```

## Running the app

You need **two terminals**: one for the backend API, one for the Streamlit UI.

**Terminal 1 — backend** (from the `backend/` folder):

```bash
cd backend
uvicorn app.main:app --reload
```

The API runs at **http://localhost:8000** (Swagger docs at **/docs**).

**Terminal 2 — frontend** (from the project root):

```bash
streamlit run frontend/app.py
```

The UI opens at **http://localhost:8501** and talks to the backend on port 8000.

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for the full concept, GenAI techniques, tech stack,
project structure, gameplay guide, API reference, testing, limitations, and the puzzle
solution guide.