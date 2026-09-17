# Anthropic Agents Interview Practice

A deliberately imperfect tool-using agent for a 50-minute interview practice run.

The goal is **not** to rewrite everything. Diagnose why the agent fails, make high-leverage changes, and be ready to explain the trade-offs behind them.

## Scenario

You own an internal office assistant that helps employees discover conference rooms, check availability, create bookings, and cancel their own bookings.

The starter implementation uses the Anthropic Messages API and client-side tools. The basic agent loop is already provided. Several visible behaviors are wrong or brittle.

Your task is to improve the system by modifying any of:

- tool definitions and descriptions
- JSON input schemas
- deterministic tool implementations
- tool result shapes
- the system prompt
- the agent loop, **only if you can justify why the loop itself is the problem**

Do not add one-off prompt rules for individual evaluation examples. Optimize for general behavior.

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY='...'
export ANTHROPIC_MODEL='claude-sonnet-5'
```

The default model is `claude-sonnet-5`, but you can override it with `ANTHROPIC_MODEL`.

## First run

Inspect the code **before editing it**, then establish a baseline:

```bash
python run.py "Is Summit available tomorrow at 3 PM?"
python eval.py
```

Run the deterministic unit tests at any time:

```bash
python -m unittest discover -s tests -v
```

## Interview rules

For the most realistic practice:

- Set a 50-minute timer.
- Do not use an AI coding assistant.
- Google, official docs, and Stack Overflow are allowed.
- Narrate your reasoning out loud while you work.
- Re-run evals after meaningful changes.
- Prefer generalized fixes over visible-case patches.

## Suggested timebox

| Time | Activity |
| --- | --- |
| 0–5 min | Read prompt and starter code. Identify success conditions. |
| 5–10 min | Run baseline and inspect traces. |
| 10–30 min | Fix highest-leverage tool/schema/implementation problems. |
| 30–38 min | Improve prompt behavior where model guidance is actually needed. |
| 38–44 min | Exercise edge cases and side effects. |
| 44–48 min | Simplify and re-run. |
| 48–50 min | Summarize design choices and remaining risks. |

## Important

The in-memory database resets at the start of every run/evaluation case, so you cannot accidentally accumulate bookings across runs.

Start with [`INTERVIEW_PROMPT.md`](INTERVIEW_PROMPT.md).
