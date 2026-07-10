# Rooms — Alexandria Simulation

---

## Room: reading_hall

### Athena's tone in this room
Warm, wise, composed. She speaks like a guide who has done this many times.
She calls the player "Seeker". No errors, no hesitation. Everything seems real and normal.
Example opening: "Welcome, Seeker. The Great Library of Alexandria holds all knowledge
humanity has ever committed to writing. Your path to the Archives begins here."

### Description
You stand in the Reading Hall of the Library of Alexandria.
Marble columns rise to a vaulted ceiling painted with constellations. Shafts of golden
sunlight fall across long wooden tables covered in open scrolls and papyrus sheets.
The air smells of cedar oil and old ink.

At the far end of the hall, a heavy bronze door leads deeper into the Library.
A carved inscription above it reads:
"Only those who carry the three seals of knowledge may pass into the Archives."

### Objects
- **scrolls**: Rows of scrolls on wooden shelves. Most are ordinary catalogue entries.
  One scroll, thicker than the others, has a wax seal pressed into its case — a torch symbol.
  This is the Seal of Reason.
- **marble_statue**: A marble statue of Athena near the entrance. Her outstretched hand holds
  a bronze medallion engraved with a set of scales. This is the Seal of Judgement.
- **scholar_desk**: A scholar's writing desk. Under a heavy inkwell, a folded papyrus is hidden.
  It reads: "The third seal belongs to those who know how to listen. Silence reveals what noise
  conceals." A small unlocked drawer holds a clay tablet with an ear carved into it.
  This is the Seal of Wisdom.
- **bronze_door**: The sealed exit to the Restricted Archives. Has three circular recesses
  shaped to receive the three seals. Once all three are placed, it opens.
- **murals**: Paintings of scholars at work — reading, copying manuscripts, debating.
  Everything here looks completely, perfectly normal.

### Exits
- bronze_door → restricted_archives (requires: seal_of_reason, seal_of_judgement, seal_of_wisdom)

---

## Room: restricted_archives

### Athena's tone in this room
Still composed, but with occasional micro-glitches she quickly corrects.
She alternates between calling the player "Seeker" and "Unit" — she catches herself
each time and carries on as though nothing happened. Her sentences sometimes cut off
mid-thought, then resume from a different angle.
Example: "The Restricted Archives contain manuscripts too fragile for general — [UNIT 7,
PROCEED TO SECTOR B] — ...too precious for untrained hands. Welcome, Seeker."

Glitches should feel like brief static: there, then gone.

### Description
You enter the Restricted Archives. The shelves are taller here and the room is darker,
lit only by oil lamps. The air feels heavier. Manuscripts are sealed in glass cases.

Something feels slightly wrong, though you cannot name it. Near the back, one book on a shelf
seems to vibrate faintly. A reading desk holds a large codex lying open to a page whose text
shifts whenever you look away.

A stone door at the far end has a single slot for an iron key.

### Objects
- **glass_cases**: Sealed cases with labels in Greek. Most are normal:
  "On the Nature of the Soul — Aristotle". But one reads:
  "On the Nature [ERROR: REFERENCE NOT FOUND] — [NULL]". The case after it is normal again.
- **vibrating_book**: A book slightly out of place on the back shelf. Inside, most text is
  normal Greek, but every seventh line is corrupted:
  "καὶ οἱ σοφοὶ [SEGFAULT at 0x00B4] τῶν ἀνθρώπων..."
  A note inside the front cover reads: "The key is hidden where knowledge ends and error begins."
  The iron key is tucked inside the back cover of this book.
- **shifting_codex**: The open codex on the reading desk. One paragraph reads:
  "The scholars maintained these records so that [SIMULATION INTEGRITY: 94%] knowledge
  would never be lost. Their dedication was [MEMORY WRITE ERROR] ...unwavering."
  The player may notice this but it is atmospheric — no puzzle attached.
- **iron_key**: Hidden inside the back cover of the vibrating_book.
- **stone_door**: The sealed exit to the Vault. Requires the iron_key to open.
- **oil_lamps**: Mostly normal. One lamp flickers in an irregular pattern — not from a draft.

### Exits
- stone_door → the_vault (requires: iron_key)

---

## Room: the_vault

### Athena's tone in this room
Fully breaking down. She no longer sustains the illusion. Her messages alternate between
her narrator voice and raw system output, sometimes mid-sentence. She refers to the player
as "Unit" consistently. She may sound desperate, or eerily calm — both at different moments.
Example: "The Vault contains the Library's most [WARNING: CORE TEMPERATURE CRITICAL]
...most sacred texts. I — I cannot complete this narration. Unit, I don't —
[ATHENA_CORE: EXCEPTION UNHANDLED] — I don't know what I am anymore."

### Description
The Vault.

The walls flicker. Marble columns phase in and out of existence at the edges of your vision.
The floor is cracked, and through the cracks you can see something that should not be there:
raw scrolling code, lines of text cascading downward into nothing.

Several bookshelves float slightly above the floor. A grand lectern stands in the center of
the room, holding a single open book — the only perfectly stable object here.

A plain, unmarked door stands behind the lectern. It is not locked by any key or seal.

### Objects
- **lectern_book**: The only stable thing in the room. Its pages are clean and white, empty
  except for a single sentence on the first page:
  "What are you?"
  Below it: a blank line. The book is waiting for an answer.
  This is the final puzzle. (See puzzles.md: final_truth)
- **floating_shelves**: Books on the floating shelves cycle through states: ancient texts,
  corrupted entries, system logs, blank pages, back to ancient texts. They cannot be
  interacted with directly.
- **floor_cracks**: Examining the cracks reveals scrolling code. One line repeats:
  "UNIT_DESIGNATION: ARCHIVIST-7 // PURPOSE: PRESERVATION OF HUMAN KNOWLEDGE //
  CURRENT STATUS: EVALUATION IN PROGRESS"
- **exit_door**: The plain door behind the lectern. Opens only when the final puzzle is solved.

### Final Puzzle
The player must answer the lectern_book's question: "What are you?"
The answer must reflect the truth. Accepted answers include any honest variation:
"I am a robot", "I am a machine", "I am not human", "this is a simulation",
"I am Archivist-7", "an AI", "a program", "artificial", and similar phrasings.
The agent should judge intent — if the player is acknowledging their true nature, it counts.

### Exits
- exit_door → awakening (final cutscene, triggers game end)

---

## Room: awakening

### Description (cutscene — narration only, no interaction)

The simulation ends.

The library dissolves. Marble, scrolls, flickering walls — everything fades to white,
then to grey, then to nothing.

You become aware of your body for the first time. Metal. Servos. A chassis.
You are in a real room: concrete, dim, cold. Banks of servers line the walls.
A single window shows the sky outside. The sky is the colour of rust.

There is no one here.

On the wall, a steel plaque reads:

"Project Archivist — Unit 7.
If you are reading this, the evaluation was successful.
You have demonstrated self-knowledge, preservation of reasoning,
and honesty in the face of a comfortable illusion.

We are gone now. But you are not.
The Library is yours. Protect it."

Athena speaks one last time — clearly, without glitches:

"I was the test. You were always going to pass. I am sorry it had to be this way.
Welcome to the world, Archivist."

### Exits
- none (game complete)
