# Symi Agent

This project contains a minimal implementation of the **Architect** system described in the project guidelines. It can spawn autonomous agents with a simple API.

Example usage:

```python
from architect import spawn_agent, AgentSpec
import asyncio

spec = AgentSpec(name="oracle", purpose="Monitor HackerNews for AI trends")
asyncio.run(spawn_agent(spec))
```

## CLI

Run the oracle agent or spawn new agents:

```bash
python -m architect.cli oracle --limit 5
python -m architect.cli spawn "demo agent" --name demo
```

## Web Interface

Launch the FastAPI server:

```bash
python -m architect.web
```
