"""SOFI OODA Agent — CLI entry point and main runner."""

import argparse
import asyncio
import logging
import os
import sys
import yaml

from core.agent import SOFIAgent

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_logging(config: dict):
    level = getattr(logging, config.get("logging", {}).get("level", "INFO"), logging.INFO)
    fmt = config.get("logging", {}).get("format", "text")

    handlers = [logging.StreamHandler()]
    log_file = config.get("logging", {}).get("file")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s" if fmt == "text"
               else "%(message)s",
        handlers=handlers,
    )


def find_config(path: str) -> str:
    """Resolve config path, with fallbacks."""
    if os.path.exists(path):
        return os.path.abspath(path)

    # Same dir as script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, path)
    if os.path.exists(candidate):
        return candidate

    # Default config.yaml
    candidate = os.path.join(script_dir, "config.yaml")
    if os.path.exists(candidate):
        return candidate

    raise FileNotFoundError(f"Config not found: {path}")


async def main_async(args):
    config_path = find_config(args.config)
    with open(config_path) as f:
        config = yaml.safe_load(f)

    setup_logging(config)
    project_root = config.get("agent", {}).get("project_root", os.getcwd())

    agent = SOFIAgent(config, project_root)

    if args.once:
        # Single cycle with manual trigger
        print(f"SOFI OODA Agent — single cycle (config: {config_path})")
        print(f"Tools: {', '.join(agent.toolbox.list_tools())}")
        print("Waiting for event (stub: no event sources configured)...")
        print("Run with --daemon for continuous operation with webhooks/file watchers.")
    else:
        print(f"SOFI OODA Agent — daemon mode (config: {config_path})")
        print(f"EventBus started — waiting for events...")
        try:
            await agent.run()
        except KeyboardInterrupt:
            print("\nShutdown requested.")
            agent.stop()


def main():
    parser = argparse.ArgumentParser(description="SOFI OODA Autonomous Agent")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--once", action="store_true", help="Single cycle (test)")
    parser.add_argument("--daemon", action="store_true", help="Continuous event-driven loop")
    parser.add_argument("--budget", type=int, help="Override daily token budget", default=None)
    args = parser.parse_args()

    # If --budget passed, inject into config
    if args.budget:
        config_path = find_config(args.config)
        with open(config_path) as f:
            config = yaml.safe_load(f)
        config.setdefault("reasoning", {})["daily_token_limit"] = args.budget
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        print(f"Daily token budget set to: {args.budget}")

    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("Stopped.")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
