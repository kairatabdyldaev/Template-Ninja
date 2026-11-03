import pytest
from django.test import Client

pytestmark = pytest.mark.django_db(transaction=True)


class TestHealthChecks:
    def test_reports_database_connectivity(self) -> None:
        response = Client().get("/healthchecks/")

        assert response.status_code == 200
        assert response.json() == {"postgresql": True}
