# Deploying
Pushing to `main` or a `claude/**` branch runs `.github/workflows/deploy.yml`, which deploys that exact commit to the shared EC2 instance (`i-00966cc1ee771d0cc`, us-west-1) through SSM using keyless GitHub OIDC (role `tap-genius-github-deploy`).

Layout on the instance: girl_game = `game` service on :80; Tap Genius = `tap-genius` service on :8081. A separate security group (`tap-genius-web`) admits CloudFront only on 8081.
`bootstrap.sh` documents the one-time AWS setup (already applied). Game state is in memory, so deploys/restarts end Tap Genius games in progress (girl_game is unaffected).

## Activity log
`server.js` appends anonymous events (rooms, joins, games, errors, a 5-minute "how busy" snapshot) to
`/var/log/tap-genius/events-YYYY-MM-DD.jsonl` (UTC days), one JSON object per line. No nicknames, photos or IP addresses.

- **Totals:** https://tap.alkouri.com/stats (any user name; the password is the `STATS_KEY` repository secret, applied on the next deploy).
- **Long-term copy:** `ship-logs.sh` runs hourly (`tap-genius-logs.timer`) and uploads each day, gzipped, to
  `s3://tap-genius-logs-405433667541/events/YYYY/MM/`. The instance keeps 30 days. If an upload fails
  (`journalctl -u tap-genius-logs`) the files simply wait on the instance and are retried the next hour.
- **Reading it:** `aws s3 cp --recursive s3://tap-genius-logs-405433667541/events/2026/11/ . && zcat *.gz | grep game_start`
