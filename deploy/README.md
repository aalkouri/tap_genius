# Deploying
Pushing to `main` or a `claude/**` branch runs `.github/workflows/deploy.yml`, which deploys that exact commit to the shared EC2 instance (`i-00966cc1ee771d0cc`, us-west-1) through SSM using keyless GitHub OIDC (role `tap-genius-github-deploy`).

Layout on the instance: girl_game = `game` service on :80; Tap Genius = `tap-genius` service on :8081. A separate security group (`tap-genius-web`) admits CloudFront only on 8081.
`bootstrap.sh` documents the one-time AWS setup (already applied). Game state is in memory, so deploys/restarts end Tap Genius games in progress (girl_game is unaffected).
