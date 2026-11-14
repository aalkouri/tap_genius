# Deploying
Pushing to `main` or a `claude/**` branch runs `.github/workflows/deploy.yml`, which deploys that exact commit to the EC2 game server through SSM using keyless GitHub OIDC.

## One-time AWS setup
Run `deploy/bootstrap.sh` with admin credentials. It creates: SSM instance role/profile, a CloudFront-only security group, a t3.micro AL2023 instance with Node + a `game` systemd unit, an Elastic IP, a CloudFront distribution, and the `tap-genius-github-deploy` OIDC role (reusing the existing GitHub OIDC provider). It then writes the instance id into the workflow — commit that change.

Note: game state is in memory, so deploys/restarts end any games in progress.
