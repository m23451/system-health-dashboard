from app import app


def get(path):
    return app.test_client().get(path)


def test_health_returns_up():
    r = get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "UP"


def test_version_returns_version():
    r = get("/version")
    assert r.status_code == 200
    assert "version" in r.get_json()


def test_environment_reads_env_var(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    r = get("/environment")
    assert r.status_code == 200
    assert r.get_json()["environment"] == "test"
