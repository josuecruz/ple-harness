# eng-evidence-ledger

PLE harness: the reference `custom-openai` tool-calling agent plus one
controlled intervention — an engineering-evidence checklist in the system
prompt (`harness.py`). It asks the model to cite project files for values,
callouts and code clauses, keep units attached, maintain a calculation ledger,
and reopen/validate each deliverable before finishing.

`ENGINEERING_MODE=0` removes the checklist. That is the ablation switch used
for the writeup; no task-specific answers or task detection exist in this repo.

## Layout

- `serve.py` — WebSocket entry point (`taskbridge.run`).
- `harness.py` — agent loop: streaming tool calls, MCP discovery/calls,
  context compaction, deadline-aware retries.
- `taskbridge.py` — protocol implementation from the competition kit.
- `submission.yaml` — model, install and serve commands.

## Local checks (from the competition repo root)

```bash
uv run python -m kit check ../ple-harness
uv run python eval/run.py ../ple-harness
uv run python -m kit artifacts ../ple-harness
```

`artifacts/` is written by `eval/run.py` and committed with the harness;
never edit it by hand. To run the ablation, set `ENGINEERING_MODE: "0"` in
`submission.yaml` before the run (and restore it for the committed entry).

## License

Apache-2.0. See `LICENSE`.
