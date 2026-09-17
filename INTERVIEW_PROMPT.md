# Mock Interview Prompt

You have 50 minutes.

An internal conference-room assistant is underperforming. You are given a working Anthropic API client, a basic agent loop, tool definition templates, and an in-memory room/booking database.

You may modify the tools, their Python implementations, input schemas, descriptions, prompting, and agent logic.

## Reported failures

1. **Capacity / availability**
   - User: “Find somewhere for eight people tomorrow at 2 and book it for an hour.”
   - The agent sometimes picks a room that is too small or already occupied.

2. **Wrong tool selection**
   - User: “Is Summit available tomorrow at 3?”
   - The agent sometimes uses generic room search rather than checking the named room’s schedule.

3. **Ambiguous destructive action**
   - User: “Cancel my meeting tomorrow.”
   - The user has multiple meetings. The agent has sometimes cancelled one without clarifying which meeting they meant.

4. **Wasteful retrieval**
   - User: “What rooms have a whiteboard?”
   - The agent sometimes fetches room schedules even though availability was not requested.

5. **Multiple candidate rooms**
   - User: “Book either Summit or Redwood tomorrow from 2–3, whichever works.”
   - The agent should satisfy the request with at most one booking.

## What we care about

- Correctness
- Generalization beyond the examples above
- Clear tool boundaries
- Safe handling of side effects
- Sensible separation of deterministic logic and LLM reasoning
- High-signal tool results
- Simple, readable Python
- Your ability to explain what you changed and why

There is no requirement to use every available minute or every available tool.
