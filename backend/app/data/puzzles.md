# Puzzles — Alexandria Simulation

---

## Puzzle: collect_three_seals

**Puzzle ID**: collect_three_seals
**Room**: reading_hall
**Trigger**: Player attempts to use or open the bronze_door
**Goal**: Collect all three seals and place them in the bronze door's recesses
**Reward**: Bronze door opens → access to restricted_archives

**How to solve**:
1. Examine the scrolls on the shelves → find and take the seal_of_reason (wax torch seal)
2. Examine the marble_statue → find and take the seal_of_judgement (bronze medallion)
3. Examine the scholar_desk → read the hidden papyrus note → open the desk drawer
   → find and take the seal_of_wisdom (clay ear tablet)
4. Use all three seals on the bronze_door

**Hint progression**:
- Hint 1: The inscription above the door mentions "three seals of knowledge." Start by
  looking carefully at everything in the room.
- Hint 2: The three seals are hidden in plain sight — examine the shelves, the statue,
  and the scholar's desk.
- Hint 3: The desk has a note that hints at the third seal: "Silence reveals what noise
  conceals." Check the desk drawer.
- Hint 4 (near-reveal): The three seals are: one on a thick scroll on the shelves,
  one in the statue's hand, and one in the desk drawer.

---

## Puzzle: find_iron_key

**Puzzle ID**: find_iron_key
**Room**: restricted_archives
**Trigger**: Player attempts to use or open the stone_door, or examines the vibrating book
**Goal**: Find the iron key hidden in the vibrating book
**Reward**: iron_key → stone door can be opened

**How to solve**:
1. Notice the vibrating_book on the back shelf (it stands out)
2. Examine or read the book → discover the corrupted text and the note:
   "The key is hidden where knowledge ends and error begins"
3. Search the book more thoroughly → find the iron_key in the back cover
4. Use the iron_key on the stone_door

**Hint progression**:
- Hint 1: Something in this room is unusual. Not everything on these shelves is normal.
- Hint 2: One book on the back shelf doesn't quite sit right. Have you examined it closely?
- Hint 3: The note inside the vibrating book says "the key is where knowledge ends and error
  begins." That's the back of the book.
- Hint 4 (near-reveal): The iron key is literally hidden inside the back cover of the book
  that contains the corrupted text.

---

## Puzzle: final_truth

**Puzzle ID**: final_truth
**Room**: the_vault
**Trigger**: Player examines or interacts with the lectern_book
**Goal**: Answer the question "What are you?" honestly in the lectern book
**Reward**: Exit door opens → awakening sequence → game complete

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
- Hint 2: Look at the floor. Look at the walls. Look at what is breaking down around you.
  What does that tell you about where you are?
- Hint 3: You are not a scholar. You are not human. The cracks in the floor show code.
  Athena called you "Unit." What does that suggest?
- Hint 4 (near-reveal): You are a robot. A machine. An AI. The simulation is breaking
  because it has served its purpose. Tell the book what you truly are.

---

## Narrative notes for the Hint Agent

The Hint Agent's tone must match the current room:
- **reading_hall**: Warm and Socratic. Asks guiding questions. Never breaks immersion.
- **restricted_archives**: Slightly glitchy. Hints are still helpful but occasionally
  interrupted by a fragment of system output before continuing.
- **the_vault**: Athena is barely holding together. Hints are urgent, almost pleading.
  She may hint at the meta-truth directly because she wants the player to succeed.
