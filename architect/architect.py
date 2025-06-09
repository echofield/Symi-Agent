import asyncio
from .builder import weave_agent
from .parser import divine_intent
from .registry import assimilate
from .orchestrator import animate
from .evolution import begin_adaptation
from datetime import datetime as dt

class AgentSpec:
    def __init__(self, name, purpose, parent=None):
        self.name = name
        self.purpose = purpose
        self.parent = parent

async def spawn_agent(spec: AgentSpec):
    """Spawn a new agent based on the specification"""
    intent = await divine_intent(spec)
    code_artifacts = await weave_agent(intent)
    agent = await animate(code_artifacts)
    await assimilate(agent, {
        "birth_timestamp": dt.utcnow().isoformat(),
        "genealogy": getattr(agent, "inheritance_chain", []),
        "capabilities": getattr(agent, "enumerate_powers", lambda: [])(),
        "network_topology": getattr(agent, "connection_map", lambda: {})(),
    })
    asyncio.create_task(begin_adaptation(agent))
    return agent
