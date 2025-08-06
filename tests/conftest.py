import pytest

from src.api import API


@pytest.fixture(scope="session", autouse=True)
def api():
    return API()