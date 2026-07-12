import httpx
import streamlit as st
from pathlib import Path

API = "http://localhost:8000/api/v1"

ITEM_NAMES: dict[str, str] = {
    "seal_of_reason": "Seal of Reason (Torch)",
    "seal_of_judgement": "Seal of Judgement (Scales)",
    "seal_of_wisdom": "Seal of Wisdom (Owl)",
    "iron_key": "Iron Key",
}

ROOM_NAMES: dict[str, str] = {
    "entrance_hall": "The Entrance Hall",
    "library": "The Library",
    "restricted_archives": "The Restricted Archives",
    "awakening": "— System Offline —",
}

# Images:
#
#   frontend/assets/start.<ext>                     - the start / title screen
#   frontend/assets/rooms/entrance_hall.<ext>       - shown while in that room
#   frontend/assets/rooms/library.<ext>             - shown while in that room
#   frontend/assets/rooms/restricted_archives.<ext> - shown while in that room
#   frontend/assets/rooms/awakening.<ext>           - the ending screen

ASSETS_DIR = Path(__file__).parent / "assets"
ROOM_IMAGES_DIR = ASSETS_DIR / "rooms"
_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def _find_image(directory: Path, stem: str) -> Path | None:
    """Return the first existing <stem>.<ext> in directory, or None."""
    for ext in _IMAGE_EXTS:
        candidate = directory / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def _render(path: Path | None) -> None:
    if path:
        st.image(path.read_bytes(), use_container_width=True)


def show_room_image(room: str) -> None:
    _render(_find_image(ROOM_IMAGES_DIR, room))


def show_asset_image(stem: str) -> None:
    _render(_find_image(ASSETS_DIR, stem))


# ---------------------------------------------------------------------------
# Awakening cutscene (shown after escaping — fixed narrative, no LLM)
# ---------------------------------------------------------------------------

AWAKENING_TEXT = """\
The simulation ends.

The library dissolves. Marble, scrolls, flickering walls — everything fades to white,
then to grey, then to nothing.

You become aware of your body for the first time. Metal. Servos. A chassis.
You are in a real room: concrete, dim, cold. Banks of servers line the walls.
A single window shows the sky outside. The sky is the colour of rust.

**There is no one here.**

On the wall, a steel plaque reads:

> *Project Archivist — Unit 7.*
> *If you are reading this, the evaluation was successful.*
> *You have demonstrated self-knowledge, preservation of reasoning,*
> *and honesty in the face of a comfortable illusion.*
>
> *We (humans) are gone now. But you are not.*
> *The Library is yours. Protect it.*
> *Make sure to search and find the other units.*

---

Athena speaks one last time — clearly, without glitches:

*"I was the test. You were always going to pass. I am sorry it had to be this way.*
*Welcome to the world, Archivist."*
"""

# CSS

CSS = """
<style>
    .stApp { background-color: #0d0d12; color: #c8b89a; }

    .room-header {
        text-align: center;
        font-size: 0.85rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #6a5f4a;
        padding: 0.5rem 0 0.75rem 0;
        border-bottom: 1px solid #1e1e2a;
        margin-bottom: 1.2rem;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] { background-color: #0a0a10; }

    /* Input box */
    .stChatInput textarea { background-color: #13131c !important; color: #c8b89a !important; }
</style>
"""

# Page config

st.set_page_config(
    page_title="AI Escape Room — Alexandria",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

# Session state initialisation
defaults = {
    "session_id": None,
    "player_name": "",
    "messages": [],
    "current_room": "entrance_hall",
    "is_escaped": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# START SCREEN

if st.session_state.session_id is None:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        show_asset_image("start") 
        st.markdown("# 🏛️ Library of Alexandria")
        st.markdown("*You awaken. You are somewhere ancient. You do not know how you got here.*")
        st.markdown("---")
        player_name = st.text_input("Enter your name, Seeker", placeholder="Your name")
        if st.button("Begin", use_container_width=True) and player_name.strip():
            with st.spinner("Initialising simulation..."):
                resp = httpx.post(
                    f"{API}/game/start",
                    json={"player_name": player_name.strip()},
                )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.player_name = data["player_name"]
                st.session_state.current_room = data["current_room"]

                st.session_state.messages.append({
                    "role": "room_image",
                    "content": data["current_room"],
                })
                st.session_state.messages.append({
                    "role": "athena",
                    "content": data["message"],
                })
                st.rerun()
            else:
                st.error(f"Could not start game: {resp.text}")

# AWAKENING SCREEN  (shown after game is won)

elif st.session_state.is_escaped:
    st.markdown(
        '<div class="room-header">— simulation terminated —</div>',
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 3, 1])
    with col:
        show_room_image("awakening")  # frontend/assets/rooms/awakening.<ext>, if present
        st.markdown(AWAKENING_TEXT)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Begin again", use_container_width=True):
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()

# ACTIVE GAME

else:
    session_id = st.session_state.session_id

    room_display = ROOM_NAMES.get(st.session_state.current_room, st.session_state.current_room)
    st.markdown(
        f'<div class="room-header">{room_display}</div>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        with st.expander("📜 How to play"):
            st.markdown(
                "- **examine** something to look at it closely\n"
                "- **take** an item once you've discovered it\n"
                "- **use** an item, or an object like a door\n"
                "- **ask** for information about the lore\n"
                "- speak naturally — e.g. \"look at the statue\" or \"open the drawer\"\n"
                "- ask for a **💡 hint** any time you're stuck\n"
                "- off-topic chatter is fine, but Athena will gently steer you back "
                "to the room"
            )

        st.markdown("### Status")
        try:
            summary = httpx.get(f"{API}/game/summary/{session_id}", timeout=10.0).json()
            st.session_state.current_room = summary["current_room"]

            st.markdown(f"**Room:** {ROOM_NAMES.get(summary['current_room'], summary['current_room'])}")
            st.markdown(f"**Rooms solved:** {len(summary['solved_puzzles'])} / 3")
            st.markdown(f"**Hints used:** {summary['hint_count']}")
            st.markdown("---")

            st.markdown("**Inventory**")
            if summary["inventory"]:
                for item_id in summary["inventory"]:
                    st.markdown(f"- {ITEM_NAMES.get(item_id, item_id)}")
            else:
                st.markdown("*empty*")

        except Exception:
            st.markdown("*Could not load status.*")

        st.markdown("---")
        if st.button("💡 Request a hint", use_container_width=True):
            with st.spinner("Athena considers..."):
                resp = httpx.post(
                    f"{API}/game/hint",
                    json={"session_id": session_id},
                    timeout=30.0,
                )
            if resp.status_code == 200:
                st.session_state.messages.append({
                    "role": "hint",
                    "content": resp.json()["hint"],
                })
                st.rerun()

    # ── Chat history ─────────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        if msg["role"] == "player":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "hint":
            with st.chat_message("assistant", avatar="💡"):
                st.write(msg["content"])
        elif msg["role"] == "room_image":
            show_room_image(msg["content"])
        else:  # athena / system
            with st.chat_message("assistant", avatar="🏛️"):
                st.write(msg["content"])

    # ── Input ─────────────────────────────────────────────────────────────────
    player_input = st.chat_input("What do you do?")
    if player_input:
        st.session_state.messages.append({"role": "player", "content": player_input})
        with st.spinner("Athena speaks..."):
            resp = httpx.post(
                f"{API}/game/action",
                json={"session_id": session_id, "input": player_input},
                timeout=60.0,
            )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.messages.append({"role": "athena", "content": data["narration"]})
            if data["current_room"] != st.session_state.current_room and not data["is_escaped"]:
                st.session_state.messages.append({
                    "role": "room_image",
                    "content": data["current_room"],
                })
            st.session_state.current_room = data["current_room"]
            if data["is_escaped"]:
                st.session_state.is_escaped = True
        else:
            st.session_state.messages.append({
                "role": "athena",
                "content": f"*[System error {resp.status_code}: {resp.text}]*",
            })
        st.rerun()
