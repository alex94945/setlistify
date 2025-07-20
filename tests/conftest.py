import pytest
from src.agent import trace_provider

@pytest.fixture(scope="session", autouse=True)
def shutdown_tracer_provider():
    """Ensure the tracer provider is shut down after the test session."""
    yield
    print("\nShutting down OpenTelemetry tracer provider...")
    trace_provider.shutdown()
    print("Tracer provider shut down.")
