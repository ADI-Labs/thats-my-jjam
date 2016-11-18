import pytest


@pytest.yield_fixture(scope="session")
def app():
    from app import app
    yield app.test_client()
