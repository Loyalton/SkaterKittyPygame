# SkaterKittyPygame

Version: 0.3.0 - performance + touch-screen release.

## What changed in 0.3.0
- Game speed no longer depends on frame rate (fixed 60 ticks/second); jump height is the same on 30, 60 and 120 Hz screens.
- Touch controls: PUSH (d), BRAKE (a), JUMP (space), GRIND (shift). They appear after the first touch.
- Smaller download (graphics + audio roughly halved), less drawing per frame, cached text, music streamed.
- Async main loop (required by pygbag).

## Art specs (unchanged)
All art was modified in photoshop. Brightness / Contrast: -14 / -25.
Button has a rectangle with 50% opacity and 100 degree rounded corner. Colors: #309de0 (button), #79e030 (controls), #e0304a (objective).
Notes: graphics/sky.jpg is a JPEG copy of the old sky.png; bgBirds.png and bgPowerLines.png are cropped to their visible rows (offsets are BG_Y in main.py).
