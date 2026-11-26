"""Connect Codex's loopback HTTP transport to the relay's Unix socket."""

import select
import socket
import socketserver
from threading import Thread

from coloph_agent_runtime.worker import main


class Forward(socketserver.BaseRequestHandler):
    def handle(self):
        with socket.socket(socket.AF_UNIX) as relay:
            relay.connect("/relay/responses.sock")
            peers = {self.request: relay, relay: self.request}
            while peers:
                ready, _, _ = select.select(list(peers), [], [], 300)
                if not ready:
                    return
                for source in ready:
                    target = peers[source]
                    data = source.recv(65536)
                    if data:
                        target.sendall(data)
                    else:
                        target.shutdown(socket.SHUT_WR)
                        del peers[source]


if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("127.0.0.1", 8765), Forward) as server:
        server.daemon_threads = True
        Thread(target=server.serve_forever, daemon=True).start()
        main()
