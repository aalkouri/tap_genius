# ⚡ Tap Genius
Real-time multiplayer trivia for phones. One player hosts and shares a 4-letter room code; friends join and race to tap the right answer (faster = more points, 500–1000 per question).
Node + WebSocket server, plain HTML/JS client — same stack as `girl_game`.

Run locally: `npm install && PORT=8080 node server.js`, open `http://localhost:8080` (open a few tabs to play).

## Hosting (same pattern as girl_game, shared server)
Runs on the same EC2 `t3.micro` (us-west-1) as girl_game: Island Night on :80, Tap Genius on :8081 (systemd `tap-genius`, `/opt/tap-genius`). CloudFront gives HTTPS + WebSockets at **https://tg.alkouri.com** (girl_game stays at game.alkouri.com). Pushes to `main` or `claude/**` deploy via GitHub Actions → OIDC → SSM (no stored secrets). See `deploy/README.md`.

## Customize
- Questions: `questions.json` (`q`, choices `c`, correct index `a`)
- Round length / count / room size: constants at top of `server.js`
