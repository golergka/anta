"""Send text-only Codex inference requests to the OpenAI Responses API."""

import http.client
import json
import os
import socketserver
from http.server import BaseHTTPRequestHandler

from smoke_responses import response_events

SOCKET = "/relay/responses.sock"
ROUTE = "/v1/responses"
MAX_BYTES = 8 * 1024 * 1024
REQUEST_FIELDS = {
    "model",
    "instructions",
    "input",
    "tools",
    "tool_choice",
    "parallel_tool_calls",
    "reasoning",
    "stream",
    "store",
    "include",
    "text",
    "prompt_cache_key",
    "client_metadata",
    "stream_options",
    "service_tier",
}
ITEM_TYPES = {
    "message",
    "input_text",
    "output_text",
    "refusal",
    "reasoning",
    "reasoning_text",
    "function_call",
    "function_call_output",
    "custom_tool_call",
    "custom_tool_call_output",
    "tool_search_call",
    "tool_search_output",
}


def text_input(items):
    if isinstance(items, str):
        return True
    if not isinstance(items, list):
        return False
    return all(
        isinstance(item, dict)
        and item.get("type", "message") in ITEM_TYPES
        and ("tools" not in item or local_tools(item["tools"]))
        and (
            item.get("type") != "tool_search_call" or item.get("execution") == "client"
        )
        and all(
            text_input(item[key])
            for key in ("content", "output")
            if key in item
            and not (
                key == "content"
                and item[key] is None
                and item.get("type") == "reasoning"
            )
        )
        for item in items
    )


def local_tools(tools):
    return isinstance(tools, list) and all(local_tool(tool) for tool in tools)


def local_tool(tool):
    if not isinstance(tool, dict):
        return False
    if tool.get("type") == "namespace":
        return local_tools(tool.get("tools"))
    if tool.get("type") == "tool_search":
        return tool.get("execution") == "client"
    return tool.get("type") in {"function", "custom"}


def inference_request(payload, model):
    if not isinstance(payload, dict) or payload.keys() - REQUEST_FIELDS:
        raise ValueError("Unexpected Responses request fields")
    if payload.get("model") != model:
        raise ValueError("Unexpected model")
    if not text_input(payload.get("input")):
        raise ValueError("Only text input and local tool results are allowed")
    if not local_tools(payload.get("tools", [])):
        raise ValueError("Only local tool definitions are allowed")
    return {**payload, "store": False}


class Relay(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(300)
        super().setup()

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path != ROUTE:
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BYTES or self.headers.get("Transfer-Encoding"):
                self.send_error(413)
                return
            payload = inference_request(
                json.loads(self.rfile.read(length)), os.environ["ANTA_BENCHMARK_MODEL"]
            )
        except (ValueError, RecursionError) as error:
            self.send_error(400, explain=str(error))
            return

        if os.environ.get("ANTA_BENCHMARK_OFFLINE") == "1":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            self.wfile.write(response_events(payload))
            return

        upstream = http.client.HTTPSConnection("api.openai.com", timeout=300)
        try:
            upstream.request(
                "POST",
                ROUTE,
                body=json.dumps(payload),
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "Content-Type": "application/json",
                },
            )
            response = upstream.getresponse()
        except (OSError, http.client.HTTPException):
            upstream.close()
            self.send_error(502)
            return
        try:
            if response.status in {401, 403}:
                self.send_error(
                    response.status, explain="OpenAI rejected the relay credentials"
                )
                return
            self.send_response(response.status)
            self.send_header(
                "Content-Type", response.getheader("Content-Type", "application/json")
            )
            self.end_headers()
            while chunk := response.read1(65536):
                self.wfile.write(chunk)
        except (OSError, http.client.HTTPException):
            return
        finally:
            upstream.close()


if __name__ == "__main__":
    with socketserver.ThreadingUnixStreamServer(SOCKET, Relay) as server:
        os.chmod(SOCKET, 0o600)
        server.daemon_threads = True
        server.serve_forever()
