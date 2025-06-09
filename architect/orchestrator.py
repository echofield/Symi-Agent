class Agent:
    def __init__(self, name, purpose):
        self.name = name
        self.purpose = purpose

    def enumerate_powers(self):
        return ['api', 'cli']

    def connection_map(self):
        return {}

import importlib
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def animate(code_artifacts):
    """Instantiate the agent from generated code on disk."""
    name = code_artifacts["name"]
    path = Path(code_artifacts.get("path", ""))
    if path:
        sys.path.insert(0, str(path / "src"))
    try:
        module = importlib.import_module(f"{name}.agent")
        agent_cls = getattr(module, f"{name.title()}Agent")
        instance = agent_cls()
        return instance
    except Exception as exc:  # pragma: no cover - dynamic
        logger.error("Failed to animate agent %s: %s", name, exc)
        return Agent(name, code_artifacts.get("purpose", ""))
