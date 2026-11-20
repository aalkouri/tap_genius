# Deploying

Every push to `main` goes live automatically on **games-server** within about a minute.

How it works (all on games-server, as the `deploy` user):
- `~/tap-genius-cron.sh` runs every minute from the `deploy` user's crontab. It calls `~/tap-genius-pull.sh`.
- `tap-genius-pull.sh` asks GitHub for the commit on `main`. If it hasn't been deployed yet, it:
  1. downloads that exact commit and checks `server.js` and `public/app.js` for syntax errors;
  2. keeps a copy of the running version;
  3. installs `server.js words.json questions public package.json package-lock.json` into `/opt/tap-genius` and restarts the `tap-genius` service;
  4. waits up to 40 s for `http://127.0.0.1:8081/healthz`. If it doesn't answer, it restores the previous version.
- If `server.js` starts reading a new file, add it to the `cp` line in `~/tap-genius-pull.sh` on the server. Otherwise the file won't be deployed.
- Real deploys and failures are logged to `~/tap-genius-deploy/deploy.log`. The last deployed commit is in `~/tap-genius-deploy/last-sha`.

Deploy right now instead of waiting for the minute:

    ssh games-server 'bash ~/tap-genius-pull.sh'

Redeploy the same commit again: add `--force`.

Layout on games-server: Caddy serves https and proxies `tap.alkouri.com` to the `tap-genius` service on 127.0.0.1:8081. It proxies `island.alkouri.com` (Island Night, the `game` service) to 127.0.0.1:3000. Game state is in memory, so a deploy or restart ends Tap Genius games in progress. Island Night is unaffected.

## Activity log
`server.js` appends anonymous events (rooms, joins, games, errors, a 5-minute "how busy" snapshot) to
`/var/log/tap-genius/events-YYYY-MM-DD.jsonl` (UTC days), one JSON object per line. No nicknames, photos or IP addresses.
The files stay on games-server; nothing deletes them yet.

- **Totals:** https://tap.alkouri.com/stats (any user name). The password is read from `/etc/tap-genius/stats.key` on the server (root-only). To change it, edit that file as root and restart `tap-genius`. The old `STATS_KEY` GitHub secret is no longer used.
- **Reading it:** `ssh games-server 'cat /var/log/tap-genius/events-2026-11-20.jsonl' | grep game_start`

## Leftovers from the AWS setup
`bootstrap.sh`, `ship-logs.sh` and `tap-genius-logs.service` / `.timer` belong to the old EC2 setup, and none of them run on games-server. Days up to 2026-11-19 were copied to `s3://tap-genius-logs-405433667541/events/YYYY/MM/`, and newer days are not.
