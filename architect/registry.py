import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def assimilate(agent: Any, metadata: Dict, registry_path: Path = Path("memory/state.json")) -> None:
    """Register the agent in the system catalog persisting to ``registry_path``."""
    registry_path.parent.mkdir(exist_ok=True)

    name = metadata.get("name") or getattr(agent, "name", None) or getattr(agent, "get", lambda k, d=None: None)("name")
    if not name:
        logger.error("Cannot register agent without a name")
        return

    state: Dict[str, Dict] = {}
    if registry_path.exists():
        with open(registry_path) as f:
            state = json.load(f)

    entry = state.get(name, {})
    if "created" not in entry:
        entry["created"] = datetime.utcnow().isoformat()
    entry.update(metadata)
    state[name] = entry

    with open(registry_path, "w") as f:
        json.dump(state, f, indent=2)

    logger.info("Registered agent %s", name)
