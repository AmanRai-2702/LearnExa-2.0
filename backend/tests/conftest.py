import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """A fake browser that talks to our app directly, with no real server.

    A fixture is a helper that pytest builds and hands to any test that lists
    its name as a parameter. Because it lives in conftest.py, every test file
    can use it without importing it.
    """
    return TestClient(app)