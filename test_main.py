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

@pytest.fixture
def test_application():
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
    return data



    
    
def test_create_application(test_application):
    
    assert test_application["company"] == "Test Company"
    assert test_application["role"] == "Data Engineer"
    assert test_application["status"] == "Applied"
    
    application_id = test_application["id"]
    
    history_response = client.get(
    f"/applications/{application_id}/history"
)

    assert history_response.status_code == 200
    
    history = history_response.json()
    
    assert len(history) == 1
    assert history[0]["status"] == "Applied"
    
def test_patch_non_status_application(test_application):
    application_id = test_application["id"]
    
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
    
    
    
    
def test_patch_application(test_application):
    application_id = test_application["id"]
    
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
    
def test_patch_nonexistent_application():
    response = client.patch(
        "/applications/99999999999",
        json={
            "status": "Interview"
        }
    )
    
    assert response.status_code == 404
    
def test_patch_required_field_to_null(test_application):
    application_id = test_application["id"]
    response = client.patch(
        f"/applications/{application_id}",
        json={
            "status":None
        }
    )
    
    assert response.status_code == 422
    
def test_post_invalid_status():
    response = client.post(
        "/applications",
        json={
            "company": "Test Company",
            "role": "Data Engineer",
            "status": "Saved"
        }
    )
    
    assert response.status_code == 422
    
@pytest.mark.parametrize(
    "invalid_status",
    ["Saved", "Pending", "Unknown"]
)
def test_post_invalid_status(invalid_status):
    response = client.post(
        "/applications",
        json={
            "company": "Test Company",
            "role": "Data Engineer",
            "status": invalid_status
        }
    )

    assert response.status_code == 422
    
def test_delete_application_cascades_history(test_application):
    delete_response = client.delete(
        f"/applications/{test_application["id"]}"
    )
    
    assert delete_response.status_code == 200
    
    get_response = client.get(
        f"/applications/{test_application["id"]}"
    )
    
    assert get_response.status_code == 404
    
    get_history_response = client.get(
        f"/applications/{test_application["id"]}/history"
    )
    
    assert get_history_response == 404