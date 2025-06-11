import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import typer

from .agents.oracle import OracleAgent
from .builder import create_agent_files
from .metrics import init_sentry 
from agents.codex_architect.cli import main as codex_main
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)
init_sentry(os.getenv("SENTRY_DSN"))

app = typer.Typer(help="Architect Agent System CLI")

STATE_PATH = Path("memory/state.json")
AGENTS_DIR = Path("agents")
CONFIG_PATH = Path("config.json")

AGENTS_DIR.mkdir(exist_ok=True)
STATE_PATH.parent.mkdir(exist_ok=True)


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_state(name: str, update: Dict[str, Any]) -> None:
    state: Dict[str, Any] = {}
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            state = json.load(f)
    entry = state.setdefault(
        name,
        {
            "purpose": update.get("purpose", ""),
            "created": datetime.utcnow().isoformat(),
            "invocations": 0,
            "last_run": None,
        },
    )
    update.pop("created", None)
    entry.update(update)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def load_all_agents() -> Dict[str, Any]:
    """Return the full agent state from ``STATE_PATH``."""
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}




@app.command()
def oracle(limit: int = typer.Option(10)):
    """Run the built-in oracle agent."""
    config = load_config()
    if not config.get("llm_provider"):
        typer.echo("No LLM provider configured")
        raise typer.Exit(code=1)
    agent = OracleAgent(config)
    result = agent.run(limit)
    typer.echo(result["summary"])


@app.command()
def spawn(description: str, name: str | None = None):
    """Create a new agent from a description."""
    if not name:
        name = description.lower().replace(" ", "_")
        name = "".join(c for c in name if c.isalnum() or c == "_")[:20]

    if name == "codex_architect":
        return codex_main()

    agent_dir = create_agent_files(name, description, AGENTS_DIR)
    save_state(name, {"purpose": description, "path": str(agent_dir)})
    typer.echo(f"Created agent {name} at {agent_dir}")



@app.command("list")
def list_agents():
    """List created agents."""
    if not STATE_PATH.exists():
        typer.echo("No agents found")
        return
    state = json.loads(STATE_PATH.read_text())
    for name, info in state.items():
        typer.echo(f"{name}: {info.get('purpose')}")


if __name__ == "__main__":
    app()
