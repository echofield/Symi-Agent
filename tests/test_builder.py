from architect.builder import create_agent_files
from pathlib import Path
import pytest

def test_create_agent_files(tmp_path):
    path = create_agent_files('demo', 'Demo agent', tmp_path)
    assert (path / 'src' / 'demo' / 'agent.py').exists()
    assert (path / 'pyproject.toml').exists()

    # calling again should raise
    with pytest.raises(FileExistsError):
        create_agent_files('demo', 'Demo agent', tmp_path)
