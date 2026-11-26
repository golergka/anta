"""One sample to exercise the benchmark infrastructure."""

import re
import subprocess

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, accuracy, scorer

from workspace import DEFAULT_MODEL, docker, isolated_codex

SSR = """
import { createServer } from 'vite'

const server = await createServer({
  configFile: false,
  cacheDir: '/tmp/anta-smoke-vite',
  optimizeDeps: { noDiscovery: true },
  server: { middlewareMode: true, ws: false },
  ssr: { noExternal: ['@antadesign/anta'] },
})
try {
  await server.ssrLoadModule('/smoke.mjs')
} finally {
  await server.close()
}
"""


def verify(container):
    try:
        result = docker(
            "exec",
            container.resource_id,
            "node",
            "--input-type=module",
            "-e",
            SSR,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "explanation": "smoke.mjs timed out"}
    passed = result.returncode == 0 and bool(
        re.fullmatch(
            r"<a-button(?: [^>]*)?><a-button-label>Anta smoke</a-button-label></a-button>",
            result.stdout.strip(),
        )
    )
    return {
        "passed": passed,
        "explanation": (result.stdout if passed else result.stderr or result.stdout)[
            :1000
        ],
    }


@scorer(metrics=[accuracy()])
def smoke_score():
    async def score(state, target):
        result = state.metadata["verification"]
        return Score(
            value=CORRECT if result["passed"] else INCORRECT,
            explanation=result["explanation"],
        )

    return score


@task
def anta_smoke(agent_model: str = DEFAULT_MODEL, offline: bool = False):
    return Task(
        dataset=[
            Sample(
                id="anta-package-smoke",
                input=(
                    "Create smoke.mjs in the workspace. Use the installed Anta Button and "
                    "React server rendering to print the static markup for a button labeled "
                    "Anta smoke. The grader loads smoke.mjs through Vite SSR. "
                    "The Anta package contains its docs. The workspace has no internet access."
                ),
            )
        ],
        solver=isolated_codex(agent_model, verify, offline=offline),
        scorer=smoke_score(),
    )
