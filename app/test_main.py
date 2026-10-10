import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("greeting", [None, "Welcome"])
def test_hello(monkeypatch, greeting):
    if greeting is None:
        monkeypatch.delenv("GREETING", raising=False)
    else:
        monkeypatch.setenv("GREETING", greeting)
    response = client.get("/hello", params={"name": "X"})
    assert response.status_code == 200
    assert response.json() == {"message": f"{greeting or 'Hello'}, X"}


def test_hello_requires_name():
    assert client.get("/hello").status_code == 422


@pytest.mark.parametrize("app_version", [None, "1.2.3"])
def test_version(monkeypatch, app_version):
    if app_version is None:
        monkeypatch.delenv("APP_VERSION", raising=False)
    else:
        monkeypatch.setenv("APP_VERSION", app_version)
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": app_version or "unknown"}
