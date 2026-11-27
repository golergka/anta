"""Start a fresh Docker workspace for each Inspect sample."""

import asyncio
import json
import os
import subprocess
import time
from contextlib import ExitStack, contextmanager
from pathlib import Path
from uuid import uuid4

from coloph_agent_inspect.codex import codex_solver
from coloph_agent_runtime import CodexRunOptions
from coloph_agent_runtime.docker import DockerBackend
from inspect_ai.solver import solver

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / ".build" / "manifest.json"
WORKSPACE = Path("/workspace")
DEFAULT_MODEL = "gpt-5.4-mini"


def docker(*args, timeout=40, capture=True, check=True):
    command = ["docker", *args]
    return subprocess.run(
        command, timeout=timeout, capture_output=capture, text=True, check=check
    )


def remove_container(name):
    result = docker("rm", "-fv", name, check=False)
    if result.returncode and "No such container" not in result.stderr:
        result.check_returncode()


def wait_for_socket(name: str, path: str):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if (
            docker("exec", name, "test", "-S", path, timeout=5, check=False).returncode
            == 0
        ):
            return
        time.sleep(0.1)
    raise RuntimeError(f"Container {name} did not open {path}")


@contextmanager
def sample_workspace(model, *, offline=False):
    if not offline and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY for the Responses relay")
    if not MANIFEST.is_file():
        raise RuntimeError("Run uv run python prepare.py first")
    manifest = json.loads(MANIFEST.read_text())
    images = manifest["images"]
    name = "anta-benchmark-" + uuid4().hex
    relay_name = name + "-relay"
    socket_mount = f"type=volume,src={name},dst=/relay"
    limits = (
        "--pull=never",
        "--init",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--cpus=2",
        "--memory=2g",
        "--memory-swap=2g",
        "--pids-limit=256",
    )
    relay_config = (
        ("--network=none", "--env", "ANTA_BENCHMARK_OFFLINE=1")
        if offline
        else ("--env", "OPENAI_API_KEY")
    )
    with ExitStack() as cleanup:
        docker("volume", "create", name)
        cleanup.callback(docker, "volume", "rm", name)
        cleanup.callback(remove_container, relay_name)
        docker(
            "run",
            "-d",
            "--name",
            relay_name,
            *limits,
            "--read-only",
            "--mount",
            socket_mount,
            *relay_config,
            "--env",
            f"ANTA_BENCHMARK_MODEL={model}",
            images["relay"],
        )
        wait_for_socket(relay_name, "/relay/responses.sock")
        cleanup.callback(remove_container, name)
        docker(
            "run",
            "-d",
            "--name",
            name,
            *limits,
            "--network=none",
            "--label",
            "coloph-agent-runtime.managed=true",
            "--mount",
            socket_mount + ",readonly",
            "--mount",
            "type=volume,dst=/workspace/node_modules,readonly",
            images["worker"],
        )
        wait_for_socket(name, "/tmp/coloph-agent-runtime.sock")
        yield DockerBackend().attach(name=name), manifest


@solver
def isolated_codex(agent_model, verify, timeout=180, offline=False):
    async def solve(state, generate):
        with sample_workspace(agent_model, offline=offline) as (container, manifest):
            state.metadata.update(manifest)
            state.metadata["inference"] = "scripted" if offline else "openai"
            run = codex_solver(
                cwd=WORKSPACE,
                records=HERE / "agent-runs",
                client=container.codex(),
                options=CodexRunOptions(
                    model=agent_model,
                    sandbox="danger-full-access",
                    skip_git_repo_check=True,
                    ephemeral=True,
                    capture_events=False,
                    timeout_seconds=timeout,
                ),
            )
            state = await run(state, generate)
            state.metadata["verification"] = await asyncio.to_thread(verify, container)
        return state

    return solve
