"""Build the current checkout and prepare the benchmark images."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from workspace import HERE, MANIFEST, docker

ROOT = HERE.parents[2]


def prepare():
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT))
    subprocess.run(["pnpm", "run", "build"], cwd=ROOT, check=True)
    MANIFEST.parent.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="anta-context-", dir=MANIFEST.parent) as temporary:
        context = Path(temporary)
        packed = subprocess.check_output(
            [
                "npm",
                "pack",
                "--ignore-scripts",
                "--json",
                "--pack-destination",
                temporary,
            ],
            cwd=ROOT,
            text=True,
        )
        tarball = context / json.loads(packed)[0]["filename"]
        tarball = tarball.rename(context / "anta.tgz")
        shutil.copytree(ROOT / "src", context / "anta-source")
        shutil.copytree(
            HERE / "starter",
            context / "starter",
            ignore=shutil.ignore_patterns("node_modules", "dist"),
        )
        for file in (
            "Dockerfile",
            "codex.toml",
            "relay.py",
            "smoke_responses.py",
            "worker.py",
        ):
            shutil.copy2(HERE / file, context)
        images = {}
        for target in ("worker", "relay"):
            image_id = context / f"{target}.iid"
            docker(
                "build",
                "--load",
                "--target",
                target,
                "--iidfile",
                str(image_id),
                temporary,
                timeout=None,
                capture=False,
            )
            images[target] = image_id.read_text().strip()
        with tarball.open("rb") as packed_anta:
            digest = hashlib.file_digest(packed_anta, "sha256").hexdigest()
        manifest = {
            "images": images,
            "anta_commit": commit,
            "dirty_checkout": dirty,
            "anta_tarball_sha256": digest,
        }
        pending = context / "manifest.json"
        pending.write_text(json.dumps(manifest, indent=2) + "\n")
        pending.replace(MANIFEST)


if __name__ == "__main__":
    prepare()
