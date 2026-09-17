from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import anthropic

from .data import OfficeDB
from .prompts import SYSTEM_PROMPT
from .tools import TOOL_DEFINITIONS, execute_tool


@dataclass
class AgentResult:
    text: str
    trace: list[dict[str, Any]]
    db: OfficeDB


def _serialize_assistant_content(response: Any) -> list[dict[str, Any]]:
    return [block.model_dump() for block in response.content]


def _text_from_response(response: Any) -> str:
    return "\n".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()


def run_agent(
    user_message: str,
    *,
    db: OfficeDB | None = None,
    client: anthropic.Anthropic | None = None,
    max_turns: int = 8,
) -> AgentResult:
    db = db or OfficeDB.fresh()
    client = client or anthropic.Anthropic()
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

    messages: list[dict[str, Any]] = [
        {"role": "user", "content": user_message},
    ]
    trace: list[dict[str, Any]] = []

    for _ in range(max_turns):
        response = client.messages.create(
            model=model,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        messages.append(
            {"role": "assistant", "content": _serialize_assistant_content(response)}
        )

        if response.stop_reason != "tool_use":
            return AgentResult(text=_text_from_response(response), trace=trace, db=db)

        tool_results = []
        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue

            tool_input = dict(block.input)
            output = execute_tool(db, block.name, tool_input)
            trace.append(
                {
                    "tool": block.name,
                    "input": tool_input,
                    "output": output,
                }
            )
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output, default=str),
                }
            )

        messages.append({"role": "user", "content": tool_results})

    return AgentResult(
        text="Agent stopped after reaching the tool-turn limit.",
        trace=trace,
        db=db,
    )
