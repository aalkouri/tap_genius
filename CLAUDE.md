# Working in this repo

- **Keep `main` in step.** The owner has asked that after every pushed change, `main` is fast-forwarded to match the working branch
  (`git push origin <working-branch>:main`) without asking each time. Only fast-forward; never force-push `main`.
- **Deploys.** tap_genius runs on the DigitalOcean server `games-server` as the `tap-genius` service (live at https://tap.alkouri.com).
  There is no GitHub deploy workflow. To deploy `main`, log in as `deploy` on the server and run `bash ~/tap-genius-pull.sh`; it does
  nothing if `main` hasn't moved. The same server runs Island Night (`game` service, island.alkouri.com): never stop the server or touch that service.
- **Questions are generated.** Edit `tools/qgen/` and run `python3 tools/build_questions.py`; do not hand-edit `questions/*.json`.
