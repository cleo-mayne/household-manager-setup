"""Minimal Claude Agent SDK smoke test.

Verifies the SDK is installed and the import path / event shape match what
the rest of the scaffold expects. NO MCP, NO tools, NO Discord, NO vault —
this is the bare-metal check that has to work before anything else can.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python cleo/scripts/smoke.py

Expected: a short reply from Claude printed to stdout.

If this fails with an ImportError, the SDK isn't installed or the package
name is wrong (try `pip install claude-agent-sdk`).

If this fails with a TypeError about unknown kwargs, the SDK API has drifted
since this scaffold was written. The fix is in `cleo/src/cleo/agent.py` —
align `ClaudeAgentOptions(...)` and the event-handling loop with whatever
the installed SDK actually exposes. See cleo/DEPLOY.md "Known SDK
surface caveats".
"""

from __future__ import annotations

import asyncio
import os
import sys


async def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 2

    try:
        from claude_agent_sdk import ClaudeAgentOptions, query
    except ImportError as e:
        print(f"SDK import failed: {e}", file=sys.stderr)
        print("Try: pip install claude-agent-sdk", file=sys.stderr)
        return 3

    # Try the constructor with no kwargs first (most permissive).
    try:
        options = ClaudeAgentOptions(system_prompt="Reply with exactly: ok")
    except TypeError as e:
        print(f"ClaudeAgentOptions(system_prompt=...) failed: {e}", file=sys.stderr)
        return 4

    print("SDK import + ClaudeAgentOptions OK; running a tiny query…")

    got_any = False
    try:
        async for event in query(prompt="Say 'ok' and nothing else.", options=options):
            got_any = True
            # Probe the event shape — we don't know yet whether it's a typed
            # class (AssistantMessage / TextBlock) or a duck-typed object.
            type_name = type(event).__name__
            text = getattr(event, "text", None)
            content = getattr(event, "content", None)
            print(f"  event: {type_name}", end="")
            if text:
                print(f"  text={text[:80]!r}")
            elif content:
                # Typed-class path: content is a list of blocks.
                snippet = repr(content)[:120]
                print(f"  content={snippet}")
            else:
                print()
    except Exception as e:
        print(f"query() failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 5

    if not got_any:
        print("query() returned no events", file=sys.stderr)
        return 6

    print("\nSmoke test passed. The SDK is callable.")
    print("Next: run a pipeline foreground — `python -m cleo.scheduled.morning_brief`.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
