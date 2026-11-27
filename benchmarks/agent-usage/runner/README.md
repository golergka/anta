# Anta agent benchmark runner

This benchmark measures how coding agents use the Anta package from the current checkout.
Coloph Agent Runtime runs Codex. Coloph Agent Inspect records each run in Inspect AI.
The smoke sample asks Codex to render one Anta Button with React.

## Run the smoke sample

Use [uv](https://docs.astral.sh/uv/), Docker with Buildx, and the Node version in
[`.node-version`](../../../.node-version). Install Codex CLI 0.144.1 on the host.
Run `codex login` and sign in with ChatGPT on that machine.

From the repository root, run:

```sh
pnpm install --frozen-lockfile
cd benchmarks/agent-usage/runner
uv sync --locked
uv run python prepare.py
uv run inspect eval smoke.py --model mockllm/model
uv run inspect view
```

Run `prepare.py` again after changes to Anta, the starter app, or the worker image.
Codex uses the account's default model. Set `-T agent_model=<model>` to choose a different model.
Inspect writes scores to `logs/` and Coloph writes agent records to `agent-runs/`.

## Isolation and limitations

Codex uses the host's ChatGPT login and internet connection for model requests.
Web search and plugins are disabled. A fresh Docker worker handles commands and file operations.
The worker has loopback networking only. The Docker command stream carries tool requests and results.

The worker has a writable React and TypeScript starter app in `/workspace`.
The installed Anta package, docs, types, and source are read-only.
Anta source is available at `/opt/anta-source`.

This runner needs a trusted machine with a saved ChatGPT login and Docker.
Live runs use that account's Codex quota. The runner requires setup on each new host.
