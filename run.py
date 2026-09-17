from __future__ import annotations

import json
import sys

from src.agent import run_agent


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python run.py "your request"')

    result = run_agent(" ".join(sys.argv[1:]))
    print("\nFINAL ANSWER\n------------")
    print(result.text or "<no text>")
    print("\nTOOL TRACE\n----------")
    print(json.dumps(result.trace, indent=2, default=str))


if __name__ == "__main__":
    main()
