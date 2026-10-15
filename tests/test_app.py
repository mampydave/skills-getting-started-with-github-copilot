import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Robotics Club": {
                "description": "Build and program robots",
                "schedule": "Mondays, 3:30 PM - 4:30 PM",
                "max_participants": 5,
                "participants": ["existing@example.com"],
            }
        },
    )

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected = {
        "Robotics Club": {
            "description": "Build and program robots",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 5,
            "participants": ["existing@example.com"],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Robotics Club"}
    assert email in client.get("/activities").json()["Robotics Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Robotics Club"}
    assert email not in client.get("/activities").json()["Robotics Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = "not-registered@example.com"

    # Act
    response = client.delete(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"