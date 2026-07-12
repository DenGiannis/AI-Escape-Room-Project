# Frontend images (optional)

Drop image files here and the UI shows them automatically. Everything is optional —
if a file is missing it is silently skipped, so the app runs fine with no images.

Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp`

## Where each image appears

| File                                | Where it shows                                  |
|-------------------------------------|-------------------------------------------------|
| `assets/start.png`                  | The start / title screen (before "Begin")       |
| `assets/rooms/entrance_hall.png`    | At the top while the player is in the Entrance Hall |
| `assets/rooms/library.png`          | At the top while the player is in the Library   |
| `assets/rooms/restricted_archives.png` | At the top while in the Restricted Archives  |
| `assets/rooms/awakening.png`        | The ending screen, after the game is won        |

The room image stays visible the whole time the player is in that room, and swaps
automatically when they move to the next one.

## Tips

- Landscape / wide images look best — they are shown full width of the content column.
- Keep file sizes reasonable (a few hundred KB each) so the page stays snappy.
