from architect.metrics import agent_errors


def test_metrics_counter():
    before = agent_errors._value.get()
    agent_errors.inc()
    assert agent_errors._value.get() == before + 1
