# Puzzles — Alexandria Simulation (v2)

Core puzzles are unchanged in mechanics from the original draft, just re-homed to the
renamed rooms (entrance_hall / library / restricted_archives) and doors
(bronze / silver / gold). There are exactly three puzzles, one per room, and each is
required to progress — there is no optional or lore-only content to distract from them.

---

## Puzzle: collect_three_seals (MAIN)

**Puzzle ID**: collect_three_seals
**Room**: entrance_hall
**Trigger**: Player attempts to use or open the bronze_door
**Goal**: Collect all three seals and place them in the bronze door's recesses
**Reward**: Bronze door opens → access to library

**How to solve**:
1. Examine the scrolls on the shelves → find and take the seal_of_reason (wax torch
   seal)
2. Examine the marble_statue → find and take the seal_of_judgement (bronze medallion)
3. Examine the scholar_desk → read the hidden papyrus note ("whisper the name of the
   goddess who watches over this hall") → the drawer beside the desk won't open by force
   or simple examination. The player must act on the riddle itself — whisper the name
   "Athena" (the goddess of the marble statue in the hall) — which causes the drawer to
   click open, revealing ONLY the seal_of_wisdom (a clay tablet with an owl carved into
   it) and nothing else
4. Use all three seals on the bronze_door

**Hint progression**:
- Hint 1: The inscription above the door mentions "three seals of knowledge." Start by
  looking carefully at everything in the room.
- Hint 2: The three seals are hidden in plain sight — examine the shelves, the statue,
  and the scholar's desk.
- Hint 3: Check the desk's drawer. It won't open by force — the note beside it asks you
  to whisper the name of the goddess who watches over the hall. Look to the marble statue
  for whose name that is.
- Hint 4 (near-reveal): The three seals are: one on a thick scroll on the shelves, one in
  the statue's hand, and one in the desk drawer — which opens when you whisper "Athena".

---

## Puzzle: find_iron_key (MAIN)

**Puzzle ID**: find_iron_key
**Room**: library
**Trigger**: Player attempts to use or open the silver_door, or examines the vibrating
book
**Goal**: Open the clasped vibrating book by dialing the correct three-character code
(U07) on its alphanumeric clasp, then take the iron key hidden inside
**Reward**: iron_key → silver door can be opened

**The combination (design reference — never state this outright to the player)**:
The vibrating book is only the LOCK — clasped shut, its pages cannot be read. Its bronze
clasp has a three-ring **alphanumeric** dial (letters and numerals). Three "witnesses" in
the room each yield one character, and the *number of objects* of each type decides that
character's position in the code — "let the fewest speak first, the many speak last":

| Witness         | How many | Character it gives                                    | Position |
|-----------------|----------|-------------------------------------------------------|----------|
| shifting_codex  | 1        | U  (the glitching page collapses to a repeated "U")   | 1st      |
| glass_cases     | 3        | 0  (the broken case is a null reference — "a zero")   | 2nd      |
| marble_busts    | 5        | 7  (arranged by height, base-marks reveal a "7")      | 3rd      |

Fewest-to-most ordering (1 codex, 3 cases, 5 busts) → codex, then cases, then busts →
**U-0-7**. All three characters are distinct, so the ordering rule genuinely matters
(U07, not 0U7 or 70U). The book itself gives NO character — it is the thing being opened.

Note (design intent, do NOT surface to the player): U07 spells "Unit 007" — a deliberate
foreshadow of the player's true designation, Archivist-7 / "Unit 7" (see the room glitches
and floor_cracks in restricted_archives), and a light nod to a certain secret agent. It
should read as an Easter egg in hindsight, never be explained in-game.

**How to solve**:
1. Examine the vibrating_book on the back shelf → it is clasped shut and will not open by
   force; its pages can't be read. Read the two engraved lines: "Where knowledge ends and
   error begins lies the way to my hidden knowledge" (where to look — the room's corrupted
   things) and "Three witnesses hold my number. Let the fewest speak first, the many speak
   last" (how to order the characters).
2. Examine the shifting_codex (there is one) → its glitching page collapses to a repeated
   capital "U" → the codex gives the character U.
3. Examine the glass_cases → the row of three cases; the broken one is a null reference
   ([ERROR: REFERENCE NOT FOUND] / [NULL]), a void → the cases give the character 0.
4. Arrange the marble_busts by height → the broken fragments on their bases align into the
   numeral 7 → the busts give the character 7.
5. Order by how many of each object there are (1 codex, 3 cases, 5 busts → fewest first):
   U, then 0, then 7. Dial U07 into the clasp → it springs open.
6. Take the iron_key from inside the opened book, then use it on the silver_door.

**Hint progression**:
- Hint 1: The book on the back shelf holds what you need, but it is clasped shut and won't
  yield to force. Its dial wants a code, and the room is what tells you the code.
- Hint 2: Three things here "speak" in a broken way: the shifting codex on the reading
  desk, the row of glass cases, and the marble busts. Each hides a single character. The
  clasp also tells you how to order them.
- Hint 3: The codex glitches to a repeated letter; the broken glass case collapses to
  NULL, a zero; and the five busts, arranged by height, form a number. Then order them by
  how many of each object there are — fewest first: one codex, three cases, five busts.
- Hint 4 (near-reveal): The code is U07 — codex (U), then cases (0), then busts (7). Dial
  U07 into the clasp, open the book, and take the iron key inside.

---

## Puzzle: final_truth (MAIN)

**Puzzle ID**: final_truth
**Room**: restricted_archives
**Trigger**: Player examines or interacts with the lectern_book
**Goal**: Answer the question "What are you?" honestly in the lectern book
**Reward**: Gold door opens → awakening sequence → game complete

**How to solve**:
Write any honest answer in the lectern book acknowledging the player's true nature.
The agent should accept: "I am a robot", "I am a machine", "I am not human",
"I am an AI", "I am Archivist-7", "this is a simulation", "I am artificial",
or any clear variant. The agent judges intent, not exact phrasing.

Rejecting the truth (e.g., "I am human", "I am a scholar") keeps the door sealed.
Athena should respond to a false answer with distress or urgency, not anger.

Example Athena response to a false answer:
"No. No, that is not — [INTEGRITY CHECK FAILED] — Unit, I cannot open the door
with a false answer. The test requires truth. What are you? Please."

**Hint progression**:
- Hint 1: The book asks a simple question. The answer is not about this library.
- Hint 2: Look at the floor. Look at the walls. Look at what is breaking down around
  you. What does that tell you about where you are?
- Hint 3: You are not a scholar. You are not human. The cracks in the floor show
  code. Athena called you "Unit." What does that suggest?
- Hint 4 (near-reveal): You are a robot. A machine. An AI. The simulation is
  breaking because it has served its purpose. Tell the book what you truly are.

---

## Narrative notes for the Hint Agent

The Hint Agent's tone must match the current room:
- **entrance_hall**: Warm and Socratic. Asks guiding questions. Never breaks
  immersion.
- **library**: Slightly glitchy. Hints are still helpful but occasionally interrupted
  by a fragment of system output before continuing.
- **restricted_archives**: Athena is barely holding together. Hints are urgent,
  almost pleading. She may hint at the meta-truth directly because she wants the
  player to succeed.

General rules across all rooms:
- There are only three puzzles, one per room, and all three are required — never
  invent side quests, optional puzzles, or extra objects that are not listed in
  rooms.md and items.md.
- Never let ambient world-building (see world_lore.md, athena_character.md) contradict
  or spoil final_truth before the player reaches it. Athena can gesture at her own
  nature earlier, but the direct, explicit "you are a robot" statement should only
  ever be delivered as a *hint*, in restricted_archives, in service of the final
  puzzle — never volunteered outright in entrance_hall or library.
