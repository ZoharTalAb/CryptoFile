import os
import pytest

os.environ["ENVIRONMENT"] = "test"

from infrastructure.db.session import engine, Base


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Creates all tables once before tests run.
    Drops them after all tests finish.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
