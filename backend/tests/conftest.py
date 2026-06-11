import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.shared.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def seed_subjects(db_session):
    from app.modules.knowledge.models import Subject

    subjects = [
        Subject(name="语文", icon="📘", sort_order=1),
        Subject(name="数学", icon="🧮", sort_order=2),
        Subject(name="英语", icon="🔤", sort_order=3),
    ]
    db_session.add_all(subjects)
    db_session.commit()
    return subjects
