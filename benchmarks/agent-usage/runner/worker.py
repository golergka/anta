"""Run the Codex executor and expose it only on worker loopback."""

import os
import socket
import sys
from pathlib import Path
from threading import Thread

HOST = "127.0.0.1"
PORT = 8765


def forward():
    with socket.create_connection((HOST, PORT), timeout=3) as connection:
        connection.settimeout(None)

        def send():
            while data := sys.stdin.buffer.read1(65536):
                connection.sendall(data)
            connection.shutdown(socket.SHUT_WR)

        Thread(target=send, daemon=True).start()
        while data := connection.recv(65536):
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()


def serve():
    # Codex resolves its working directory in both processes.
    Path(os.environ["ANTA_WORKSPACE"]).symlink_to(
        "/workspace", target_is_directory=True
    )
    os.execvp("codex", ["codex", "exec-server", "--listen", f"ws://{HOST}:{PORT}"])


if __name__ == "__main__":
    if sys.argv[1:] == ["forward"]:
        forward()
    elif sys.argv[1:] == ["ready"]:
        with socket.create_connection((HOST, PORT), timeout=1):
            pass
    else:
        serve()
