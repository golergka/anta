"""Scripted inference responses for the offline smoke sample."""

import json

WRITE_SAMPLE = """cat > smoke.mjs <<'JS'
import { Button } from '@antadesign/anta'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

console.log(renderToStaticMarkup(createElement(Button, null, 'Anta smoke')))
JS
"""


def response_events(payload):
    tool_finished = any(
        isinstance(item, dict)
        and item.get("type") == "function_call_output"
        and item.get("call_id") == "call_smoke"
        for item in payload["input"]
    )
    if tool_finished:
        response_id = "resp_smoke_2"
        item = {
            "type": "message",
            "id": "msg_smoke",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "Created smoke.mjs."}],
        }
    else:
        response_id = "resp_smoke_1"
        item = {
            "type": "function_call",
            "call_id": "call_smoke",
            "name": "exec_command",
            "arguments": json.dumps({"cmd": WRITE_SAMPLE}),
        }
    events = [
        {"type": "response.created", "response": {"id": response_id}},
        {"type": "response.output_item.done", "item": item},
        {
            "type": "response.completed",
            "response": {
                "id": response_id,
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            },
        },
    ]
    return "".join(
        f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events
    ).encode()
