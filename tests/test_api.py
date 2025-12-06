"""Tests for Belt Monitor API"""
import pytest
from fastapi.testclient import TestClient
from app.api import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data


class TestResultsEndpoint:
    def test_list_empty_results(self, client):
        response = client.get("/api/v1/results")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
    
    def test_get_nonexistent_result(self, client):
        response = client.get("/api/v1/results/nonexistent")
        assert response.status_code == 404
