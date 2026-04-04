"""
FastAPI Backend Tests for Mergington High School Activities API

Tests cover core functionality:
- GET /activities - Retrieve all activities
- POST /activities/{activity_name}/signup - Sign up for an activity
- DELETE /activities/{activity_name}/unregister - Unregister from an activity
- GET / - Root redirect
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to create a TestClient instance for each test."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """ARRANGE: No setup needed.
        ACT: Make GET request to /activities.
        ASSERT: Status code should be 200 OK.
        """
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_all_activities_returns_dict(self, client):
        """ARRANGE: No setup needed.
        ACT: Make GET request to /activities.
        ASSERT: Response should be a dictionary.
        """
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_all_activities_contains_all_activities(self, client):
        """ARRANGE: No setup needed.
        ACT: Make GET request to /activities.
        ASSERT: Response should contain all 9 predefined activities.
        """
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Music Ensemble",
            "Debate Team",
            "Science Club",
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """ARRANGE: No setup needed.
        ACT: Make GET request to /activities.
        ASSERT: Each activity should have required fields.
        """
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]

        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_valid_activity_returns_200(self, client):
        """ARRANGE: No setup needed.
        ACT: Make POST request to sign up for a valid activity.
        ASSERT: Status code should be 200 OK.
        """
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 200

    def test_signup_adds_student_to_participants(self, client):
        """ARRANGE: Student email to use for signup.
        ACT: Sign up student for an activity, then retrieve activities.
        ASSERT: Student email should appear in activity's participants list.
        """
        student_email = "newstudent@mergington.edu"
        client.post(
            "/activities/Chess Club/signup",
            params={"email": student_email},
        )
        response = client.get("/activities")
        activities = response.json()
        assert student_email in activities["Chess Club"]["participants"]

    def test_signup_for_invalid_activity_returns_404(self, client):
        """ARRANGE: Invalid activity name.
        ACT: Make POST request to sign up for non-existent activity.
        ASSERT: Status code should be 404 Not Found.
        """
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup_returns_400(self, client):
        """ARRANGE: Sign up student for an activity.
        ACT: Attempt to sign up the same student for the same activity again.
        ASSERT: Status code should be 400 Bad Request.
        """
        student_email = "duplicate@mergington.edu"
        client.post(
            "/activities/Programming Class/signup",
            params={"email": student_email},
        )
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": student_email},
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_response_contains_message(self, client):
        """ARRANGE: Student email to use for signup.
        ACT: Sign up student for an activity.
        ASSERT: Response should contain a success message.
        """
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": "success@mergington.edu"},
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_registered_student_returns_200(self, client):
        """ARRANGE: Sign up a student for an activity.
        ACT: Delete that student from the activity.
        ASSERT: Status code should be 200 OK.
        """
        student_email = "student_to_remove@mergington.edu"
        client.post(
            "/activities/Soccer Club/signup",
            params={"email": student_email},
        )
        response = client.delete(
            "/activities/Soccer Club/unregister",
            params={"email": student_email},
        )
        assert response.status_code == 200

    def test_unregister_removes_student_from_participants(self, client):
        """ARRANGE: Sign up a student for an activity.
        ACT: Unregister that student, then retrieve activities.
        ASSERT: Student email should not appear in activity's participants list.
        """
        student_email = "to_be_removed@mergington.edu"
        client.post(
            "/activities/Art Club/signup",
            params={"email": student_email},
        )
        client.delete(
            "/activities/Art Club/unregister",
            params={"email": student_email},
        )
        response = client.get("/activities")
        activities = response.json()
        assert student_email not in activities["Art Club"]["participants"]

    def test_unregister_nonexistent_student_returns_400(self, client):
        """ARRANGE: A student not signed up for the activity.
        ACT: Attempt to unregister that student.
        ASSERT: Status code should be 400 Bad Request.
        """
        response = client.delete(
            "/activities/Music Ensemble/unregister",
            params={"email": "notregistered@mergington.edu"},
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_from_invalid_activity_returns_404(self, client):
        """ARRANGE: Invalid activity name.
        ACT: Attempt to unregister from non-existent activity.
        ASSERT: Status code should be 404 Not Found.
        """
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_response_contains_message(self, client):
        """ARRANGE: Sign up a student for an activity.
        ACT: Unregister that student.
        ASSERT: Response should contain a success message.
        """
        student_email = "farewell@mergington.edu"
        client.post(
            "/activities/Debate Team/signup",
            params={"email": student_email},
        )
        response = client.delete(
            "/activities/Debate Team/unregister",
            params={"email": student_email},
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]


class TestRoot:
    """Tests for GET / endpoint."""

    def test_root_returns_redirect(self, client):
        """ARRANGE: No setup needed.
        ACT: Make GET request to root endpoint.
        ASSERT: Status code should be 307 Temporary Redirect.
        """
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_root_redirects_to_static_index(self, client):
        """ARRANGE: No setup needed.
        ACT: Make GET request to root endpoint and follow redirects.
        ASSERT: Final response should come from static/index.html.
        """
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
