import os
import pytest
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models import JobApplication

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DB")
port = os.getenv("POSTGRES_PORT")


DATABASE_URL = f"postgresql+psycopg://{user}:{password}@localhost:{port}/{database}"

test_engine = create_engine(url=DATABASE_URL, echo=True)

TestingSessionLocal = sessionmaker(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db 
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_test_database():
    db = TestingSessionLocal()

    db.execute(delete(JobApplication))
    db.commit()

    db.close()

    yield

    db = TestingSessionLocal()

    db.execute(delete(JobApplication))
    db.commit()

    db.close()

def test_create_application():
    response = client.post(
        "/applications",
        json={
            "company": "Test Company",
            "role": "Data Engineer",
            "status": "Applied"
        }
    )
    
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["company"] == "Test Company"
    assert data["role"] == "Data Engineer"
    assert data["status"] == "Applied"
    
    application_id = data["id"]
    
    history_response = client.get(
    f"/applications/{application_id}/history"
)

    assert history_response.status_code == 200
    
    history = history_response.json()
    
    assert len(history) == 1
    assert history[0]["status"] == "Applied"
    
def test_patch_non_status_application():
    post_response = client.post(
        "/applications",
        json={
            "company": "Test Company",
            "role": "Data Engineer",
            "status": "Applied"
        }
    )
    
    assert post_response.status_code == 200
    
    data = post_response.json()
    assert data["company"] == "Test Company"
    assert data["role"] == "Data Engineer"
    assert data["status"] == "Applied"
    
    application_id = data["id"]
    
    patch_response = client.patch(
        f"/applications/{application_id}",
        json={
            "company": "Ace"
        }
    )
    
    assert patch_response.status_code == 200
    
    patch_data = patch_response.json()
    assert patch_data["company"] == "Ace"
    
    history_response = client.get(
        f"/applications/{application_id}/history" 
    )
    
    assert history_response.status_code == 200
    
    history_data = history_response.json()
    
    assert len(history_data) == 1
    
    
    
    
def test_patch_application():
    post_response = client.post(
        "/applications",
        json={
            "company": "Test Company",
            "role": "Data Engineer",
            "status": "Applied"
        }
    )
    
    assert post_response.status_code == 200
    
    data = post_response.json()
    assert data["company"] == "Test Company"
    assert data["role"] == "Data Engineer"
    assert data["status"] == "Applied"
    
    application_id = data["id"]
    
    patch_response = client.patch(
        f"/applications/{application_id}",
        json={
            "status": "Interview"
        }
    )
    
    assert patch_response.status_code == 200
    
    patch_data = patch_response.json()
    assert patch_data["status"] == "Interview"
    
    history_response = client.get(
        f"/applications/{application_id}/history" 
    )
    
    assert history_response.status_code == 200
    
    history_data = history_response.json()
    
    assert len(history_data) == 2
    assert [d["status"] for d in history_data] == ["Applied", "Interview"]    
    
    