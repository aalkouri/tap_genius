# Working in this repo

- **Keep `main` in step.** The owner has asked that after every pushed change, `main` is fast-forwarded to match the working branch
  (`git push origin <working-branch>:main`) without asking each time. Only fast-forward; never force-push `main`.
- **Pushing deploys.** A push to `main` or any `claude/**` branch runs `.github/workflows/deploy.yml`, which copies the commit to the
  shared EC2 instance and restarts the `tap-genius` service (live at https://tap.alkouri.com). The same instance runs another game
  (`game` service, island.alkouri.com) — never stop the instance or touch that service.
- **Questions are generated.** Edit `tools/qgen/` and run `python3 tools/build_questions.py`; do not hand-edit `questions/*.json`.
