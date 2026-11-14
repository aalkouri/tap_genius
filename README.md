# ⚡ Tap Genius

Real-time multiplayer trivia. One person hosts and shares a 4-letter room code; friends join from their phones and race to tap the right answer (faster = more points).

## Architecture (all AWS, serverless)

| Piece | Service |
|---|---|
| Static web app | S3 (private) + CloudFront (OAC, HTTPS) |
| Real-time messaging | API Gateway WebSocket API |
| Game logic | Lambda (Node 20) — `backend/src/handler.mjs` |
| Rooms / players / connections | DynamoDB (on-demand, TTL cleanup after 4h) |
| Infra as code | AWS SAM — `template.yaml` |

Game flow: `create`/`join` → `start` → per question: `answer` (all answered or timer ends → `reveal`) → host `next` → final scores → `again`.
The correct answer is never sent to clients until reveal.

## Deploy

```bash
./scripts/deploy.sh        # sam build/deploy, writes frontend/config.js, syncs S3, invalidates CloudFront
```
Prereqs: AWS CLI + SAM CLI + credentials. Region defaults to `us-east-1` (`AWS_REGION` to change).
CI: `.github/workflows/deploy.yml` deploys on push to `main` using an OIDC role in secret `AWS_DEPLOY_ROLE_ARN`.

## Customize
- Questions: `backend/src/questions.json` (`q`, choices `c`, correct index `a`)
- Round length / count: constants at top of `handler.mjs`
- Custom domain: add an ACM cert (us-east-1) + alias on the CloudFront distribution + Route 53 record.
