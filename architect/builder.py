"""Utilities for constructing agent file structures."""

from pathlib import Path
from typing import Dict


def generate_agent_template(name: str, description: str) -> Dict[str, str]:
    """Return source templates for a new agent."""
    agent_code = f'''"""{name} Agent"""
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class {name.title()}Agent:
    def __init__(self, config: Dict | None = None):
        self.config = config or {{}}
        self.memory = Path("memory/state.json")

    def run(self, **kwargs) -> Dict[str, Any]:
        logger.info("running {name}")
        self._log()
        return {{"status": "ok", "timestamp": datetime.utcnow().isoformat()}}

    def _log(self) -> None:
        state = {{}}
        if self.memory.exists():
            state = json.loads(self.memory.read_text())
        entry = state.setdefault(
            "{name}",
            {{"purpose": "{description}", "created": datetime.utcnow().isoformat(), "invocations": 0, "last_run": None}},
        )
        entry["invocations"] += 1
        entry["last_run"] = datetime.utcnow().isoformat()
        self.memory.write_text(json.dumps(state, indent=2))
'''

    cli_code = f'''import typer
from .agent import {name.title()}Agent

app = typer.Typer()


@app.command()
def run():
    agent = {name.title()}Agent()
    result = agent.run()
    print(result)


if __name__ == "__main__":
    app()
'''

    api_code = f'''from fastapi import FastAPI
from .agent import {name.title()}Agent

app = FastAPI()


@app.post("/run")
async def run():
    agent = {name.title()}Agent()
    return agent.run()
'''

    pyproject = f'''[tool.poetry]
name = "{name}-agent"
version = "0.1.0"
description = "{description}"

[tool.poetry.dependencies]
python = "^3.10"
typer = "^0.9.0"
fastapi = "^0.110.0"
uvicorn = "^0.29.0"

[tool.poetry.scripts]
{name} = "{name}.cli:app"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
'''

    return {
        "agent_code": agent_code,
        "cli_code": cli_code,
        "api_code": api_code,
        "pyproject": pyproject,
    }


def create_agent_files(name: str, description: str, agents_dir: Path = Path("agents")) -> Path:
    """Create a directory with boilerplate agent files."""

    tmpl = generate_agent_template(name, description)
    agent_dir = agents_dir / name
    if agent_dir.exists():
        raise FileExistsError(str(agent_dir))

    src_dir = agent_dir / "src" / name
    (agent_dir / "src").mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)

    # write source files
    (src_dir / "__init__.py").write_text("")
    (src_dir / "agent.py").write_text(tmpl["agent_code"])
    (src_dir / "cli.py").write_text(tmpl["cli_code"])
    (src_dir / "api.py").write_text(tmpl["api_code"])

    # simple worker and models placeholders
    (src_dir / "worker.py").write_text("""# background tasks for the agent\n""")
    (src_dir / "models.py").write_text("""# data models for the agent\n""")

    # project files
    (agent_dir / "pyproject.toml").write_text(tmpl["pyproject"])
    (agent_dir / "README.md").write_text(f"# {name.title()} Agent\n\n{description}\n")

    # tests
    tests_dir = agent_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "test_dummy.py").write_text("def test_dummy():\n    assert True\n")

    return agent_dir


async def weave_agent(intent, agents_dir: Path = Path("agents")) -> Dict[str, str]:
    """Generate file structure for an agent and return basic metadata."""

    name = intent.get("name")
    description = intent.get("purpose", "")
    agent_dir = create_agent_files(name, description, agents_dir)
    return {"name": name, "purpose": description, "path": str(agent_dir)}
