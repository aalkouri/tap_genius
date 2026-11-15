# ⚡ Tap Genius
Real-time multiplayer party game for phones. One player hosts a game (Trivia or Mini Games); everyone else taps **Join game** and picks it from a live list of open games — no codes to type. Trivia: race to tap the right answer (faster = more points, 500–1000 per question). Mini Games: quick challenges — whack-a-mole, RC Mayhem (a lane-per-player RC car race with logs, boulders and bridges that go up and down) Picture This (one player draws a secret word live, everyone else races to guess it; needs 2+ players), Hot Potato (throw a bomb with a hidden fuse by tapping other players' heads; needs 3+) and Copy Cat (repeat a growing pattern of musical pads; one mistake and you're out).

In the Mini Games lobby the host picks which games to play (even just one) and how many rounds (each game once, 1, 3 or 5).

If a phone loses its connection (locked, switched app, minimised) the server holds that player's seat for 3 minutes and the page reconnects on its own.
Node + WebSocket server, plain HTML/JS client — same stack as `girl_game`.

Run locally: `npm install && PORT=8080 node server.js`, open `http://localhost:8080` (open a few tabs to play).

## Hosting (same pattern as girl_game, shared server)
Runs on the same EC2 `t3.micro` (us-west-1) as girl_game: Island Night on :80, Tap Genius on :8081 (systemd `tap-genius`, `/opt/tap-genius`). CloudFront gives HTTPS + WebSockets at **https://tg.alkouri.com** (girl_game stays at game.alkouri.com). Pushes to `main` or `claude/**` deploy via GitHub Actions → OIDC → SSM (no stored secrets). See `deploy/README.md`.

## Customize
- Questions: `questions.json` (`q`, choices `c`, correct index `a`)
- Round length / count / room size: constants at top of `server.js`
