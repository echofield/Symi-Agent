from prometheus_client import Counter, Histogram
import logging
from typing import Optional

# Prometheus metrics
agent_errors = Counter("agent_errors_total", "Total agent errors")
agent_invocations = Counter("agent_invocations_total", "Total agent invocations")
agent_run_seconds = Histogram("agent_run_seconds", "Agent execution duration in seconds")


def init_sentry(dsn: Optional[str]) -> None:
    """Initialize Sentry error tracking if a DSN is provided."""
    if not dsn:
        return
    try:
        import sentry_sdk  # type: ignore
        sentry_sdk.init(dsn=dsn)
    except Exception as exc:  # pragma: no cover - optional
        logging.getLogger(__name__).error("Failed to init Sentry: %s", exc)

