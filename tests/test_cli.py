import json
from pathlib import Path
from architect.cli import load_all_agents, save_state, STATE_PATH
import pytest

def test_load_all_agents(tmp_path, monkeypatch):
    path = tmp_path / 'state.json'
    monkeypatch.setattr('architect.cli.STATE_PATH', path)

    # No file -> empty dict
    assert load_all_agents() == {}

    data = {'demo': {'purpose': 'demo agent'}}
    path.write_text(json.dumps(data))
    assert load_all_agents() == data

    save_state('demo', {'invocations': 1})
    result = load_all_agents()
    assert result['demo']['invocations'] == 1


def test_save_state_preserves_created(tmp_path, monkeypatch):
    path = tmp_path / 'state.json'
    monkeypatch.setattr('architect.cli.STATE_PATH', path)

    save_state('demo', {'purpose': 'demo'})
    created1 = json.loads(path.read_text())['demo']['created']
    save_state('demo', {'invocations': 1})
    created2 = json.loads(path.read_text())['demo']['created']
    assert created1 == created2
