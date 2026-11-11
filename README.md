# SkaterKittyPygame

Version: 0.3.3 - zoomed portrait, landscape side bars, arcade top-3 leaderboard, reset when you leave.

## What changed in 0.3.3
- Phone upright (full screen): the game is zoomed in (PORTRAIT_ZOOM = 1.25, the left 80% of the world fills the width) with a black control box underneath for the pads. The score and collectibles are drawn on their own layer, so they stay exactly where they were. Menus and the end screen are not zoomed.
- Phone sideways and wide (aspect 1.95 or more): two black side bars hold the pads (left = BRAKE/PUSH, right = GRIND/JUMP) so nothing covers the game. Tablets / narrower screens keep the see-through pads on the game.
- Arcade leaderboard on the end screen: top 3 scores with 3-letter initials. First finish asks for initials (tap the arrows or type, Enter / OK), later runs only ask when they make the top 3. Scores are kept in the browser (localStorage) and, on desktop Python, in leaderboard.json. Optional shared board for everybody: see leaderboard_server.gs and LEADERBOARD_URL in main.py.
- Leaving the page, locking the phone, switching tabs or pressing Exit: the embed unloads the game (music stops, next play starts at the menu). Inside the game a JavaScript listener does the same as a backup.
- Version string is 0.3.3.

## What changed in 0.3.1
- Touch controls are two slide pads: left = BRAKE (top) / PUSH (bottom), right = GRIND (top) / JUMP (bottom). A thumb stays on its pad while sliding between zones. GRIND latches until the thumb lifts, then stays armed for GRIND_GRACE_TICKS (0.3 s) and, if you land on an obstacle, stays on until you leave it.
- Phone held upright: the window gets taller and the pads sit under the game.
- Tuning block near the top of main.py: MAX_SPEED 11.2 (80%), ACCELERATION 0.35/3, OLLIE_SCALE 0.866 (about 75% jump height).
- embed_snippet.html: tap-to-play poster (game only downloads when tapped), loading instructions, iPhone-friendly full screen.

## What changed in 0.3.0
- Game speed no longer depends on frame rate (fixed 60 ticks/second); jump height is the same on 30, 60 and 120 Hz screens.
- Touch controls: PUSH (d), BRAKE (a), JUMP (space), GRIND (shift). They appear after the first touch.
- Smaller download (graphics + audio roughly halved), less drawing per frame, cached text, music streamed.
- Async main loop (required by pygbag).

## Art specs (unchanged)
All art was modified in photoshop. Brightness / Contrast: -14 / -25.
Button has a rectangle with 50% opacity and 100 degree rounded corner. Colors: #309de0 (button), #79e030 (controls), #e0304a (objective).
Notes: graphics/sky.jpg is a JPEG copy of the old sky.png; bgBirds.png and bgPowerLines.png are cropped to their visible rows (offsets are BG_Y in main.py).
