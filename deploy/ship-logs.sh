#!/usr/bin/env bash
# Runs hourly on the instance (tap-genius-logs.timer, installed by the deploy workflow).
# Copies the activity log to S3, one gzipped object per day, and keeps only 30 days on the instance's (shared) disk.
# Today's file is uploaded again every hour; a finished day is uploaded one last time and then marked .shipped.
set -uo pipefail
DIR=/var/log/tap-genius
BUCKET=${TG_LOG_BUCKET:-tap-genius-logs-405433667541}
REGION=us-west-1
today=$(date -u +%F); rc=0
if command -v aws >/dev/null; then
  for f in "$DIR"/events-*.jsonl; do
    [ -e "$f" ] || continue
    [ -e "$f.shipped" ] && continue
    day=${f##*/events-}; day=${day%.jsonl}
    if gzip -c "$f" | aws s3 cp - "s3://$BUCKET/events/${day:0:4}/${day:5:2}/events-$day.jsonl.gz" --region "$REGION" --only-show-errors; then
      if [[ "$day" < "$today" ]]; then touch "$f.shipped"; fi
    else
      rc=1
    fi
  done
else
  echo "aws CLI is not installed: nothing was copied to S3"; rc=1
fi
find "$DIR" -name 'events-*.jsonl*' -mtime +30 -delete
exit $rc
