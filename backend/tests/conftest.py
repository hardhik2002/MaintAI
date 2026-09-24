import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path("test_maintai.db")
os.environ["MAINTAI_DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["MAINTAI_MODEL_PATH"] = "ml/artifacts/model.joblib"

from backend.app.core.database import Base, engine  # noqa: E402
from backend.app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
