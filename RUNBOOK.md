# Local runbook (PLE competition repo root: /home/local/ple)

Credentials live outside the entry, in `/home/local/ple/run.env` (never committed):

```
HF_TOKEN=hf_...                      # account that accepted the gated dataset terms
MODEL_PROXY_URL=http://localhost:4000
MODEL_PROXY_KEY=...                  # for google-cloud models, via kit/model_proxy/start.sh
# or, for a personal/local API model used only to generate development artifacts:
OPENAI_BASE_URL=https://.../v1
OPENAI_API_KEY=...
JUDGE_BASE_URL=https://.../v1        # optional local judge
JUDGE_API_KEY=...
JUDGE_MODEL=<the model actually used>
```

Commands (from `/home/local/ple`):

```bash
uv run python -m kit check ../ple-harness --env-file run.env
uv run python eval/run.py ../ple-harness --env-file run.env
uv run python -m kit artifacts ../ple-harness
uv run python eval/run.py --artifacts ../ple-harness --env-file run.env
cd ../ple-harness && python3 figures/make_figures.py runs/<run>
```

Ablation: set `ENGINEERING_MODE: "0"` in `submission.yaml`, re-run the same
tasks with the same model and budget, then restore `"1"` before the final
commit. `artifacts/` must come from the final harness; re-run it after any code
change and commit harness, artifacts and figures in one commit.
