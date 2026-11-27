# Anta agent benchmark runner

This benchmark measures how coding agents use the Anta package from the current checkout.
Coloph Agent Runtime runs Codex. Coloph Agent Inspect records each run in Inspect AI.
The smoke sample asks Codex to render one Anta Button with React.

## Run the smoke sample

Use [uv](https://docs.astral.sh/uv/), Docker with Buildx, and the Node version in
[`.node-version`](../../../.node-version).

From the repository root, run:

```sh
pnpm install --frozen-lockfile
cd benchmarks/agent-usage/runner
uv sync --locked
uv run python prepare.py
uv run inspect eval smoke.py --model mockllm/model -T offline=true
uv run inspect view
```

Run `prepare.py` again after changes to the Anta build, starter app, or container files.
Offline mode runs the real Codex CLI with scripted model responses.
For a live run, set `OPENAI_API_KEY` to a key with API credits.
Then omit `-T offline=true`.
Use `-T agent_model=<model>` to change the default model, `gpt-5.4-mini`.
Inspect writes scores to `logs/` and Coloph writes agent records to `agent-runs/`.

## Sample environment

Each sample gets a fresh, unprivileged Linux container with loopback networking only.
It has a writable React and TypeScript starter app in `/workspace`.
The runner mounts its installed dependencies, including the packed Anta build, read-only.
The package includes its docs and types. The checkout's Anta source is in `/opt/anta-source`.

A separate relay accepts text-only Responses requests over a Unix socket.
For live runs, the relay holds the API key and sends requests to OpenAI.
For offline runs, both containers have loopback networking only.
Container creation and cleanup use Docker. Coloph Agent Runtime attaches to the worker.
