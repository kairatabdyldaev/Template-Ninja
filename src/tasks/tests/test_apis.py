import pytest
from django.test import Client

from src.tasks.models import Task
from src.tasks.tests.factories import TaskFactory

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def client() -> Client:
    return Client()


class TestTaskApi:
    def test_creates_and_returns_a_task(self, client: Client) -> None:
        response = client.post(
            "/api/tasks",
            data={"title": "Buy milk", "description": "2 liters"},
            content_type="application/json",
        )

        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Buy milk"
        assert body["status"] == Task.Status.OPEN
        assert Task.objects.filter(id=body["id"]).exists()

    def test_rejects_an_empty_title(self, client: Client) -> None:
        response = client.post(
            "/api/tasks",
            data={"title": ""},
            content_type="application/json",
        )

        assert response.status_code == 422
        assert Task.objects.count() == 0

    def test_lists_tasks_with_filters(self, client: Client) -> None:
        TaskFactory(title="Open one", status=Task.Status.OPEN)
        TaskFactory(title="Done one", status=Task.Status.DONE)

        response = client.get("/api/tasks", data={"status": Task.Status.OPEN})

        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 1
        assert body["items"][0]["title"] == "Open one"

    def test_lists_tasks_with_limit_and_offset(self, client: Client) -> None:
        TaskFactory(title="First")
        TaskFactory(title="Second")

        response = client.get("/api/tasks", data={"limit": 1, "offset": 1})

        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 2
        assert len(body["items"]) == 1
        assert body["items"][0]["title"] == "First"

    def test_returns_404_for_a_missing_task(self, client: Client) -> None:
        response = client.get("/api/tasks/999999")

        assert response.status_code == 404
        assert response.json() == {"message": "Not found"}

    def test_updates_a_task(self, client: Client) -> None:
        task = TaskFactory(title="Old", description="keep")

        response = client.patch(
            f"/api/tasks/{task.id}",
            data={"title": "New"},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["title"] == "New"
        assert response.json()["description"] == "keep"

    def test_completes_a_task_once(self, client: Client) -> None:
        task = TaskFactory()

        first = client.post(f"/api/tasks/{task.id}/complete")
        second = client.post(f"/api/tasks/{task.id}/complete")

        assert first.status_code == 200
        assert first.json()["status"] == Task.Status.DONE
        assert second.status_code == 409
        assert second.json() == {"message": "Task is already done"}

    def test_openapi_describes_status_codes(self, client: Client) -> None:
        response = client.get("/api/openapi.json")

        assert response.status_code == 200
        paths = response.json()["paths"]
        assert set(paths["/api/tasks/{task_id}"]["get"]["responses"]) == {"200", "404"}
        assert set(paths["/api/tasks"]["post"]["responses"]) == {"201", "400", "422"}
        assert set(paths["/api/tasks/{task_id}"]["patch"]["responses"]) == {
            "200",
            "400",
            "404",
            "422",
        }
        assert set(paths["/api/tasks/{task_id}/complete"]["post"]["responses"]) == {
            "200",
            "404",
            "409",
        }
        assert "MessageSchema" in response.json()["components"]["schemas"]
