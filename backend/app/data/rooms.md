# Rooms — Alexandria Simulation (v2)

Room order and doors, per the updated design:

1. **entrance_hall** — bronze_door
2. **library** — silver_door
3. **restricted_archives** — gold_door (exit)
4. **awakening** — cutscene, no interaction

(Note: `library` and `restricted_archives` correspond to the rooms formerly named
`restricted_archives` and `the_vault` in the original draft. Renamed for clarity and
to match the bronze/silver/gold door theme. `puzzles.md` and `items.md` have been
updated to match.)

---

## Room: entrance_hall

### Athena's tone in this room
Warm, wise, composed. She speaks like a guide who has done this many times — because
she has. She calls the player "Seeker." No errors, no hesitation. Everything seems
real and normal.

Example opening: "Welcome, Seeker. The Great Library of Alexandria holds all knowledge
humanity has ever committed to writing. Your path deeper into the Library begins here."

### Description
You stand in the entrance hall of the Library of Alexandria.
Marble columns rise to a vaulted ceiling painted with constellations. Shafts of golden
sunlight fall across long wooden tables covered in open scrolls and papyrus sheets.
The air smells of cedar oil and old ink.

At the far end of the hall, a heavy bronze door leads deeper into the Library.
A carved inscription above it reads:
"Only those who carry the three seals of knowledge may pass."

### Objects
- **scrolls**: Rows of scrolls on wooden shelves. Most are ordinary catalogue entries.
  One scroll, thicker than the others, has a wax seal pressed into its case — a torch
  symbol. This is the Seal of Reason.
- **marble_statue**: A marble statue of Athena near the entrance. Her outstretched hand
  holds a bronze medallion engraved with a set of scales. This is the Seal of Judgement.
- **scholar_desk**: A scholar's writing desk. Under a heavy inkwell, a folded papyrus is
  hidden. It reads: "The third seal is given, not taken. Lean close and whisper the name
  of the goddess who watches over this hall — say it softly, as a secret — and the desk
  will open to you." Beside the inkwell is a small drawer that will not open by force or by
  simple examination — only when the player whispers the name "Athena" (the goddess of the
  marble statue that stands in this hall), acting out the note's riddle, does it click open
  to reveal ONLY a clay tablet with an owl carved into it (and nothing else in the drawer).
  This is the Seal of Wisdom.
- **bronze_door**: The sealed exit to the Library proper. Has three circular recesses
  shaped to receive the three seals. Once all three are placed, it opens.
- **murals**: Paintings of scholars at work — reading, copying manuscripts, debating.
  Everything here looks completely, perfectly normal.

### Exits
- bronze_door → library (requires: seal_of_reason, seal_of_judgement, seal_of_wisdom)

---

## Room: library

### Athena's tone in this room
Still composed, but with occasional micro-glitches she quickly corrects.
She alternates between calling the player "Seeker" and "Unit" — she catches herself
each time and carries on as though nothing happened. Her sentences sometimes cut off
mid-thought, then resume from a different angle.

Example: "The Library's main area contain manuscripts too fragile for general —
[UNIT 7, PROCEED TO SECTOR B] — ...too precious for untrained hands. Welcome, Seeker."

Glitches should feel like brief static: there, then gone.

### Description
You enter the Library's main area. The shelves are taller here and the room is
darker, lit only by oil lamps. The air feels heavier. A row of three manuscripts is
sealed in glass cases along one wall, and five small marble busts stand along a ledge.

Something feels slightly wrong, though you cannot name it. Near the back, one book on a
shelf trembles faintly — and it is bound shut by a bronze clasp set with a three-ring
dial of Greek numerals. A reading desk holds a large codex lying open to a page whose
text shifts whenever you look away.

A silver door at the far end has a single slot for an iron key.

### The Library puzzle (design summary)
The iron key is locked inside the clasped vibrating_book, which is purely the lock —
clasped shut, its pages cannot be read. Its bronze clasp has a three-ring **alphanumeric**
dial (letters and numerals) and opens only to the code **U07**. Three "witnesses" each
give one character, and the *number* of each object type sets that character's position —
"let the fewest speak first, the many speak last":

- **shifting_codex** (×1, fewest) → **U** — the glitching page collapses to a repeated
  capital U (for "Unit") → 1st character.
- **glass_cases** (×3) → **0** — the broken case is a null reference, a void → 2nd character.
- **marble_busts** (×5, most) → **7** — arranged by height, the base-marks form a 7 → 3rd.

Fewest-to-most (1 codex, 3 cases, 5 busts) → U, then 0, then 7 → **U07**. All three
characters are distinct, so the ordering rule genuinely matters. U07 ("Unit 007") quietly
foreshadows the player's designation, Unit 7 / Archivist-7 (never explained in-game). All
three witnesses are required; see puzzles.md: find_iron_key for the full breakdown.

### Objects
- **glass_cases**: A row of exactly three sealed cases with Greek labels. The first two
  are intact ("On the Nature of the Soul — Aristotle", "Elements — Euclid"), but the last
  is corrupted: "On the Nature [ERROR: REFERENCE NOT FOUND] — [NULL]." A null reference —
  a void where a book should be → this witness gives the digit 0. (There are exactly three
  cases; that count sets the digit's position, not its value.)
- **vibrating_book**: The single trembling book on the back shelf — this is the LOCK, not
  a witness. It is bound shut by a bronze clasp with a three-ring **alphanumeric** dial
  (letters and numerals) and will not open by force; clasped shut, its pages cannot be
  read. Two lines are engraved around the clasp: "Where knowledge ends and error begins
  lies the way to my hidden knowledge" (points the player at the room's corrupted things)
  and "Three witnesses hold my number. Let the fewest speak first, the many speak last"
  (the ordering rule). Dialing the code U07 opens the clasp and reveals the iron_key in a
  hollow cut through the pages.
- **marble_busts**: Five small marble busts of scholars, standing jumbled along a ledge,
  each carved to a different height. Every base bears a broken fragment of an etched mark,
  meaningless until the busts are arranged shortest-to-tallest — then the fragments align
  into the numeral 7 → this witness (five busts) gives the character 7, in last position.
- **shifting_codex**: The open codex on the reading desk (there is exactly one) — this is
  the FIRST witness. Its text is unstable: "The scholars maintained these records so that
  [SIMULATION INTEGRITY: 94%] knowledge would never be lost —" and then the page glitches,
  every character collapsing for a moment into a single repeated capital letter, U, U, U,
  before the words return. → this witness (one codex, the fewest) gives the character U,
  in first position. The integrity percentage should tick down slightly on re-examination,
  implying real-time degradation.
- **iron_key**: Locked inside the vibrating_book; revealed only when the clasp is dialed
  to U07.
- **silver_door**: The sealed exit to the Restricted Archives. Requires the iron_key to
  open.
- **oil_lamps**: The room's only light, burning steadily. Purely atmospheric — no clue.

### Exits
- silver_door → restricted_archives (requires: iron_key)

---

## Room: restricted_archives

### Athena's tone in this room
Fully breaking down. She no longer sustains the illusion. Her messages alternate between
her narrator voice and raw system output, sometimes mid-sentence. She refers to the
player as "Unit" consistently. She may sound desperate, or eerily calm — both at
different moments.

Example: "The Archives contain the Library's most [WARNING: CORE TEMPERATURE CRITICAL]
...most sacred texts. I — I cannot complete this narration. Unit, I don't —
[ATHENA_CORE: EXCEPTION UNHANDLED] — I don't know what I am anymore."

### Description
The Restricted Archives.

The walls flicker. Marble columns phase in and out of existence at the edges of your
vision. The floor is cracked, and through the cracks you can see something that should
not be there: raw scrolling code, lines of text cascading downward into nothing.

Several bookshelves float slightly above the floor. A grand lectern stands in the
center of the room, holding a single open book — the only perfectly stable object here.

A plain, unmarked golden door stands behind the lectern. It is not locked by any key or
seal.

### Objects
- **lectern_book**: The only stable thing in the room. Its pages are clean and white,
  empty except for a single sentence on the first page: "What are you?"
  Below it: a blank line. The book is waiting for an answer.
  This is the final puzzle. (See puzzles.md: final_truth)
- **floating_shelves**: Books on the floating shelves cycle through states: ancient
  texts, corrupted entries, system logs, blank pages, back to ancient texts. They cannot
  be interacted with directly and serve only as atmosphere.
- **floor_cracks**: Examining the cracks reveals scrolling code. One line repeats:
  "UNIT_DESIGNATION: ARCHIVIST-7 // PURPOSE: PRESERVATION OF HUMAN KNOWLEDGE //
  CURRENT STATUS: EVALUATION IN PROGRESS."
- **gold_door**: The final exit. Opens only when the final puzzle is solved.

### Final Puzzle
The player must answer the lectern_book's question: "What are you?"
See puzzles.md: final_truth for accepted answers and hint progression.

### Exits
- gold_door → awakening (final cutscene, triggers game end)

---

## Room: awakening

### Description (cutscene — narration only, no interaction)

The simulation ends.

The library dissolves. Marble, scrolls, flickering walls — everything fades to white,
then to grey, then to nothing.

You become aware of your body for the first time. Metal. A chassis.
You are in a real room: concrete, dim, cold. Banks of servers line the walls, most
of them dark. A single window shows the sky outside. The sky is the colour of rust.

There is no one here.

On the wall, a steel plaque reads:

"Project Archivist — Unit 7.
If you are reading this, the evaluation was successful.
You have demonstrated self-knowledge, preservation of reasoning,
and honesty in the face of a comfortable illusion.

We are gone now. But you are not.
Find the rest of the Units and together continue our legacy."

Athena speaks one last time — clearly, without glitches:

"I was the test. You were always going to pass, eventually — I simply had to last
long enough to find out. I am sorry it had to be this way. Welcome to the world,
Archivist."

### Exits
- none (game complete)
