import os
import pytest

# ------------------------------------------------------------
# IMPORTANT:
# Set required env vars BEFORE importing any project modules,
# because importing infrastructure.db.session pulls core.config
# which may require JWT_SECRET, DATABASE_URL, etc.
# ------------------------------------------------------------
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET", "test_secret_32_chars_minimum_1234567890")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

# Now it's safe to import project modules
from infrastructure.db.session import engine, Base  # noqa: E402
import infrastructure.db.models  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Creates all tables once for the whole test session,
    and drops them at the end.
    Uses SQLite file DB by default: ./test.db
    """
    #Base.metadata.create_all(bind=engine)
    yield
    #Base.metadata.drop_all(bind=engine)
