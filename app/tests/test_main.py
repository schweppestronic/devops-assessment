"""Tests for the config service.

Implemented with Claude Code (model: Claude Opus 5.5, effort: low).
"""

import threading

import pytest

from main import ConfigStore, create_app


@pytest.fixture
def client():
    # Fresh store per test so tests don't leak state into each other.
    app = create_app(store=ConfigStore())
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_version_default(client, monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    resp = client.get("/version")
    assert resp.status_code == 200
    assert resp.get_json() == {"version": "1.0.0"}


def test_version_from_env(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "2.3.4")
    assert client.get("/version").get_json() == {"version": "2.3.4"}


def test_env_reads_environment_variable(client, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "dev")
    resp = client.get("/env")
    assert resp.status_code == 200
    assert resp.get_json() == {"environment": "dev"}


def test_env_unset(client, monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    assert client.get("/env").get_json() == {"environment": "unknown"}


def test_config_lifecycle(client):
    payload = {"name": "database_url", "value": "postgres://example"}

    resp = client.post("/config", json=payload)
    assert resp.status_code == 201
    assert resp.get_json() == payload

    resp = client.get("/config/database_url")
    assert resp.status_code == 200
    assert resp.get_json() == payload

    resp = client.delete("/config/database_url")
    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": True}

    assert client.get("/config/database_url").status_code == 404


def test_config_overwrite(client):
    client.post("/config", json={"name": "k", "value": "v1"})
    client.post("/config", json={"name": "k", "value": "v2"})
    assert client.get("/config/k").get_json() == {"name": "k", "value": "v2"}


def test_config_empty_value_allowed(client):
    resp = client.post("/config", json={"name": "k", "value": ""})
    assert resp.status_code == 201
    assert client.get("/config/k").get_json() == {"name": "k", "value": ""}


def test_get_missing_config(client):
    resp = client.get("/config/missing")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_delete_missing_config(client):
    resp = client.delete("/config/missing")
    assert resp.status_code == 404
    assert resp.get_json() == {"deleted": False}


@pytest.mark.parametrize(
    "body",
    [
        {"value": "x"},                      # missing name
        {"name": "k"},                       # missing value
        {"name": "", "value": "x"},          # empty name
        {"name": "a/b", "value": "x"},       # not URL-safe
        {"name": "a" * 129, "value": "x"},   # name too long
        {"name": 123, "value": "x"},         # wrong type
        {"name": "k", "value": 123},         # wrong type
        {"name": "k", "value": "x" * 4097},  # value too long
        ["name", "value"],                   # not an object
    ],
)
def test_create_config_validation(client, body):
    resp = client.post("/config", json=body)
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_config_invalid_json(client):
    resp = client.post("/config", data="not json", content_type="application/json")
    assert resp.status_code == 400


def test_unknown_route_returns_json(client):
    resp = client.get("/nope")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_wrong_method_returns_json(client):
    resp = client.put("/health")
    assert resp.status_code == 405
    assert "error" in resp.get_json()


def test_store_is_thread_safe():
    store = ConfigStore()

    def writer(i):
        for j in range(200):
            store.set(f"k{i}-{j}", "v")

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(store.get(f"k{i}-{j}") == "v" for i in range(8) for j in range(200))
