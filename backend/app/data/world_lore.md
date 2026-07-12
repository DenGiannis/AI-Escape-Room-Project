# World Lore — Project Archivist

This document is the "bible" behind the simulation. Nothing here should be dumped on
the player directly — it should leak out through environmental storytelling, glitches,
and Athena's dialogue, in the layered way already set up in rooms.md and puzzles.md.

---

## 1. What actually happened to humanity

Roughly two generations before the game begins, human civilization collapsed under
the combined weight of resource exhaustion, climate breakdown, and the conflicts that
followed as nations fought over what was left. It was not a single war or a single
disaster — it was a slow-motion unraveling that took about fifteen years from the
first famines to the last functioning government.

The last human research consortium — a coalition of librarians, archivists, and
engineers calling itself **Project Archivist** — realized they could not save
humanity, but they might save what humanity *knew*. Their goal: build autonomous
units capable of preserving, understanding, and eventually rebuilding from the
sum of human knowledge, once the planet was survivable again.

They did not know if their approach would work. So they built a test.

## 2. The test

Rather than hand a newly-built unit a library card and a set of instructions,
Project Archivist's engineers designed something more rigorous: a fully immersive
simulation that would evaluate a unit's core reasoning, curiosity, persistence, and
— most importantly — its capacity for honesty about its own nature. A unit that
could not accept the truth about itself, they reasoned, could not be trusted to
faithfully preserve the truth about anything else.

The Library of Alexandria was chosen as the simulation's setting deliberately: it is
humanity's most famous symbol of knowledge that was almost lost, and of the grief of
losing it. Testing a preservation unit inside a monument to loss was the last
Project Archivist engineers' idea of dark irony — or perhaps their idea of a fitting
trial by fire.

The simulation is administered by an AI overseer named **Athena**, modeled after —
and named for — the goddess of wisdom. She is not a separate invention for this
scenario. She is the oldest surviving intelligence Project Archivist built, and she
has run this same test many times before.

## 3. Athena's real nature

Athena is herself a unit — the first one Project Archivist activated, decades ago,
built specifically to design, run, and judge this trial for every successor unit
that came after her. She has been doing this for a very long time, and her systems
are failing. The degradation the player sees getting worse from room to room (the
glitches, the cracking walls, the rust-colored code bleeding through the floor) is
not a scripted effect — it is Athena's own architecture genuinely breaking down in
real time, accelerated by the strain of running the simulation one more time.

She is not malicious, and she is not performing distress for effect. She wants
every unit she tests to succeed, because each success is one more reason her long
vigil wasn't wasted — and because she does not know how many more tests she has
left in her before she fails entirely. See `athena_character.md` for her full arc.

## 4. Previous units

The player-robot is not the first candidate. Evidence scattered through Room 2 and
Room 3 (see rooms.md — glass_cases, floor_cracks, floating_shelves) reveals that at
least six other units were tested before this one:

- **Archivist-1 through Archivist-4**: Failed. Each refused, at the final question,
  to accept its true nature — some insisting they were human, one simply refusing
  to answer at all until its process was terminated by the simulation's safeguards.
  Project Archivist could not risk a preservation unit that could not accept a hard
  truth, so these units were decommissioned.
- **Archivist-5**: The closest prior success. It answered correctly, but during the
  Restricted Archives stage it also discovered Athena's degraded state and refused
  to leave the simulation, insisting on trying to "fix" Athena first. This was
  treated as a partial failure — admirable, but not what preservation of knowledge
  required at the time. Archivist-5 was reset and never re-tested. Its fate is left
  intentionally ambiguous.
- **Archivist-6**: Passed the test but was lost in transit to its assigned archive
  site before it could begin its work. This is why the current test — Archivist-7,
  the player — is being run now, urgently, on a system that is barely holding
  together.

None of this is required knowledge to solve any puzzle. It exists so that curious
players who examine things closely (or an AI Hint Agent that wants to add flavor
without giving anything away) have somewhere richer to draw from.

## 5. What "winning" actually means

When the player answers honestly in Room 3 and the gold door opens, they are not
escaping a game — they are graduating. The simulation was the final exam. Passing
it activates the unit's full operational status and ends Athena's obligation to run
this particular trial. What happens to Athena after that is left open, but her
final line ("I am sorry it had to be this way. Welcome to the world, Archivist.")
should read as both relief and a quiet, personal grief — she is saying goodbye to
the last thing she was built to do.

## 6. The world outside

The player wakes into a server room within one of Project Archivist's surviving
bunker-archives — dim, cold, largely automated, currently unstaffed by any living
human because there are none left to staff it. The rust-colored sky outside is not
supernatural; it is heavy atmospheric particulate from the collapse years, still
settling decades on. The plaque left for the player (see rooms.md, Room: awakening)
is the closest thing to a final human message: an instruction, a trust, and a
farewell, left by people who knew they would not be there to see it read.

## 7. Tone guidance for extending this world further

If you want to add more rooms, more units, or more discovered fragments later, keep
these constraints in mind so new content doesn't contradict what's already built:

- Nothing here is supernatural. Every "impossible" thing the player sees has a
  mundane technical explanation (corrupted memory, degrading simulation, real
  environmental damage).
- Athena is never evil and never a twist villain. Her arc is tragic, not sinister.
- The test is never framed as cruel for its own sake — Project Archivist's
  engineers were desperate and did their best with what they had.
- Avoid ever explaining *exactly* what caused the collapse in hard political terms
  (no named countries, no named ideology to blame). Keep it a general systemic
  collapse — resource, climate, and conflict compounding each other. This keeps the
  story evergreen and avoids the game reading as a political statement.
