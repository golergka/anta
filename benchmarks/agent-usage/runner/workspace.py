"""Connect signed-in local Codex to a fresh, offline Docker executor."""

import asyncio
import json
import os
import subprocess
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from coloph_agent_inspect.codex import codex_solver
from coloph_agent_runtime import CodexClient, CodexRunOptions
from inspect_ai.solver import solver

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / ".build" / "manifest.json"
CODEX_VERSION = "0.144.1"


def docker(*args, timeout=40, capture=True, check=True):
    return subprocess.run(
        ["docker", *args],
        timeout=timeout,
        capture_output=capture,
        text=True,
        check=check,
    )


def local_codex_env():
    return {
        key: os.environ[key]
        for key in ("PATH", "HOME", "CODEX_HOME")
        if key in os.environ
    }


def check_login():
    env = local_codex_env()
    version = subprocess.check_output(
        ["codex", "--version"], env=env, text=True, timeout=10
    ).strip()
    if version != f"codex-cli {CODEX_VERSION}":
        raise RuntimeError(f"Install Codex CLI {CODEX_VERSION}. Found {version}.")
    status = subprocess.run(
        ["codex", "login", "status"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if (
        status.returncode
        or "Logged in using ChatGPT" not in status.stdout + status.stderr
    ):
        raise RuntimeError("Run codex login and sign in with ChatGPT on this machine")


class LocalCodex(CodexClient):
    def __init__(self, executor_url):
        super().__init__(executable=str(HERE / "codex-chatgpt"))
        self.env = {**local_codex_env(), "CODEX_EXEC_SERVER_URL": executor_url}

    def run(self, prompt, **kwargs):
        return super().run(prompt, base_env=self.env, **kwargs)


@contextmanager
def sample_workspace():
    if not MANIFEST.is_file():
        raise RuntimeError("Run uv run python prepare.py first")
    manifest = json.loads(MANIFEST.read_text())
    if "worker_image" not in manifest:
        raise RuntimeError(
            "Run uv run python prepare.py again to build the Codex executor"
        )
    name = "anta-benchmark-" + uuid4().hex
    with TemporaryDirectory(prefix="anta-codex-", dir="/tmp") as directory:
        cwd = Path(directory).resolve()
        try:
            docker(
                "run",
                "-d",
                "--name",
                name,
                "--pull=never",
                "--init",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--cpus=2",
                "--memory=2g",
                "--memory-swap=2g",
                "--pids-limit=256",
                "--network=none",
                "--env",
                f"ANTA_WORKSPACE={cwd}",
                "--mount",
                "type=volume,dst=/workspace/node_modules,readonly",
                manifest["worker_image"],
            )
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if (
                    docker(
                        "exec",
                        name,
                        "python",
                        "/opt/worker.py",
                        "ready",
                        timeout=5,
                        check=False,
                    ).returncode
                    == 0
                ):
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError(
                    f"Worker did not start: {docker('logs', name).stderr}"
                )
            yield name, cwd, manifest
        finally:
            result = docker("rm", "-fv", name, check=False)
            if result.returncode and "No such container" not in result.stderr:
                result.check_returncode()


async def copy_stream(source, destination):
    while data := await source.read(65536):
        destination.write(data)
        await destination.drain()


@asynccontextmanager
async def executor_connection(container):
    connections = set()

    async def forward(reader, writer):
        task = asyncio.current_task()
        connections.add(task)
        child = None
        pumps = []
        try:
            child = await asyncio.create_subprocess_exec(
                "docker",
                "exec",
                "-i",
                container,
                "python",
                "/opt/worker.py",
                "forward",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            pumps = [
                asyncio.create_task(copy_stream(reader, child.stdin)),
                asyncio.create_task(copy_stream(child.stdout, writer)),
            ]
            await asyncio.wait(pumps, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for pump in pumps:
                pump.cancel()
            await asyncio.gather(*pumps, return_exceptions=True)
            writer.close()
            if child is not None:
                child.stdin.close()
                try:
                    await asyncio.wait_for(child.wait(), timeout=2)
                except TimeoutError:
                    child.kill()
                    await child.wait()
            connections.discard(task)

    async with await asyncio.start_server(forward, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        try:
            yield f"ws://127.0.0.1:{port}"
        finally:
            server.close()
            active = tuple(connections)
            for connection in active:
                connection.cancel()
            await asyncio.gather(*active, return_exceptions=True)
            await server.wait_closed()


@solver
def isolated_codex(agent_model, verify, timeout=180):
    async def solve(state, generate):
        check_login()
        with sample_workspace() as (container, cwd, manifest):
            state.metadata.update(manifest)
            state.metadata["inference"] = "chatgpt"
            async with executor_connection(container) as executor_url:
                run = codex_solver(
                    cwd=cwd,
                    records=HERE / "agent-runs",
                    client=LocalCodex(executor_url),
                    options=CodexRunOptions(
                        model=agent_model,
                        sandbox="danger-full-access",
                        skip_git_repo_check=True,
                        ignore_user_config=True,
                        ephemeral=True,
                        capture_events=False,
                        timeout_seconds=timeout,
                    ),
                )
                state = await run(state, generate)
            state.metadata["verification"] = await asyncio.to_thread(verify, container)
        return state

    return solve
