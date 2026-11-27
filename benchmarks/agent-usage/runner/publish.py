"""Publish one Inspect log and its viewer to a Hugging Face Static Space."""

import argparse
import hashlib
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from dotenv import load_dotenv
from huggingface_hub import HfApi, get_token
from inspect_ai.log import bundle_log_dir, read_eval_log


def publish(log: Path, api: HfApi, space_id: str) -> str:
    header = read_eval_log(str(log), header_only=True)
    if header.status == "started":
        raise ValueError("Wait for the Inspect run to finish before you publish it.")

    space = api.space_info(space_id)
    if space.sdk != "static" or not space.host or space.private:
        raise ValueError(f"Use a public Hugging Face Static HTML Space for {space_id}.")

    with TemporaryDirectory() as temp_dir:
        staging = Path(temp_dir)
        logs = staging / "logs"
        logs.mkdir()
        snapshot = logs / f"run{log.suffix}"
        shutil.copyfile(log, snapshot)
        with snapshot.open("rb") as file:
            run_id = hashlib.file_digest(file, "sha256").hexdigest()

        destination = f"runs/{run_id}"
        viewer = staging / "viewer"
        bundle_log_dir(log_dir=str(logs), output_dir=str(viewer))
        if not (viewer / "logs" / snapshot.name).is_file():
            raise ValueError(f"Inspect did not include {log.name} in the viewer bundle.")

        api.upload_folder(
            repo_id=space_id,
            repo_type="space",
            folder_path=viewer,
            path_in_repo=destination,
            commit_message=f"Publish Inspect run {run_id[:12]}",
        )

    return f"{space.host.rstrip('/')}/{destination}/index.html"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="Path to one finished Inspect log.")
    args = parser.parse_args()

    load_dotenv(Path(__file__).with_name(".env"))
    space_id = os.getenv("ANTA_HF_SPACE")
    if not space_id:
        parser.error("Set ANTA_HF_SPACE to the Space ID (owner/name).")
    token = get_token()
    if not token:
        parser.error("Set HF_TOKEN in the runner .env or sign in with hf auth login.")
    if not args.log.is_file() or args.log.suffix not in {".eval", ".json"}:
        parser.error("Supply one Inspect .eval or .json file.")

    print(publish(args.log, HfApi(token=token), space_id))


if __name__ == "__main__":
    main()
