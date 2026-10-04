#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo
============================

A minimal harness demonstrating long-running autonomous coding with Claude.
This script implements the two-agent pattern (initializer + coding agent) and
incorporates all the strategies from the long-running agents guide.

Example Usage:
    python autonomous_agent_demo.py --project-dir ./claude_clone_demo
    python autonomous_agent_demo.py --project-dir ./claude_clone_demo --max-iterations 5
"""

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
# IMPORTANT: Must be called BEFORE importing other modules that read env vars at load time
load_dotenv()


def apply_auth_mode() -> str:
    """
    Pick between Claude subscription and API billing via AUTH_MODE.

    - subscription: ignore ANTHROPIC_API_KEY so the Claude CLI login is used
    - api: require ANTHROPIC_API_KEY
    - auto (default): leave the environment untouched (a key, if set, wins)
    """
    mode = os.environ.get("AUTH_MODE", "auto").strip().lower()
    if mode == "subscription":
        os.environ.pop("ANTHROPIC_API_KEY", None)
    elif mode == "api":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("AUTH_MODE=api but ANTHROPIC_API_KEY is not set (.env or shell)")
    elif mode != "auto":
        raise SystemExit(f"Invalid AUTH_MODE={mode!r} (use subscription, api or auto)")
    return mode


AUTH_MODE = apply_auth_mode()

from agent import run_autonomous_agent


# Configuration
# DEFAULT_MODEL = "claude-opus-4-5-20251101"
DEFAULT_MODEL = "claude-sonnet-4-6"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent Demo - Long-running agent harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start fresh project
  python autonomous_agent_demo.py --project-dir ./claude_clone

  # Use a specific model
  python autonomous_agent_demo.py --project-dir ./claude_clone --model claude-sonnet-4-6

  # Limit iterations for testing
  python autonomous_agent_demo.py --project-dir ./claude_clone --max-iterations 5

  # Continue existing project
  python autonomous_agent_demo.py --project-dir ./claude_clone

Authentication (set AUTH_MODE in .env or the shell):
  AUTH_MODE=subscription  Use the Claude CLI login (run 'claude login'); ignores ANTHROPIC_API_KEY
  AUTH_MODE=api           Use ANTHROPIC_API_KEY (API billing)
  AUTH_MODE=auto          Default: an ANTHROPIC_API_KEY, if set, takes precedence
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./autonomous_demo_project"),
        help="Directory for the project (default: generations/autonomous_demo_project). Relative paths automatically placed in generations/ directory.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Claude model to use (default: {DEFAULT_MODEL})",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Authentication: see apply_auth_mode(). Without an API key the Claude SDK
    # uses the Claude CLI login (set up by start.bat/start.sh).
    using_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    print(f"Auth: AUTH_MODE={AUTH_MODE} -> {'API key' if using_api else 'Claude subscription'}")

    # Automatically place projects in generations/ directory unless already specified
    project_dir = args.project_dir
    if not str(project_dir).startswith("generations/"):
        # Convert relative paths to be under generations/
        if project_dir.is_absolute():
            # If absolute path, use as-is
            pass
        else:
            # Prepend generations/ to relative paths
            project_dir = Path("generations") / project_dir

    try:
        # Run the agent (MCP server handles feature database)
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                model=args.model,
                max_iterations=args.max_iterations,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print("To resume, run the same command again")
    except Exception as e:
        print(f"\nFatal error: {e}")
        raise


if __name__ == "__main__":
    main()
