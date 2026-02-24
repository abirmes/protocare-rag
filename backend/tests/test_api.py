import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.models import Base

engine_test = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


client = TestClient(app)

USER = {"username": "dr_martin", "email": "martin@hopital.fr", "password": "securepass123"}


def register():
    return client.post("/auth/register", json=USER)


def login():
    return client.post("/auth/login", data={"username": USER["email"], "password": USER["password"]})



def test_register_success():
    r = register()
    assert r.status_code == 201
    assert r.json()["email"] == USER["email"]
    assert r.json()["role"] == "medecin"


def test_register_duplicate_email():
    register()
    r = client.post("/auth/register", json={**USER, "username": "autre"})
    assert r.status_code == 400


def test_login_success():
    register()
    r = login()
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password():
    register()
    r = client.post("/auth/login", data={"username": USER["email"], "password": "wrong"})
    assert r.status_code == 401


def test_me_authenticated():
    register()
    token = login().json()["access_token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == USER["username"]


def test_me_unauthenticated():
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_health():
    r = client.get("/health")
    assert r.status_code == 200