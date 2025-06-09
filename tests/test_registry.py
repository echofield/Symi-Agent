import json
import asyncio
from pathlib import Path
from architect.registry import assimilate

class Dummy:
    def __init__(self, name):
        self.name = name

def test_assimilate(tmp_path):
    path = tmp_path / "state.json"
    asyncio.run(assimilate(Dummy("demo"), {"purpose": "demo"}, registry_path=path))
    data = json.loads(path.read_text())
    assert data["demo"]["purpose"] == "demo"
