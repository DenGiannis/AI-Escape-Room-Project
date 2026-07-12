from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    # In-memory DB. StaticPool keeps a single shared connection so the schema and
    # data persist for the whole test, across the app's and the test's access.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    # Make the app use our in-memory session instead of the real database.
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
