import importlib
from architect.orchestrator import animate
from architect.builder import create_agent_files
import asyncio

def test_animate(tmp_path):
    path = create_agent_files('demo', 'Demo agent', tmp_path)
    artifacts = {'name': 'demo', 'purpose': 'Demo agent', 'path': str(path)}
    agent = asyncio.run(animate(artifacts))
    assert agent.__class__.__name__ == 'DemoAgent'
