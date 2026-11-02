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

def test_metrics_endpoint_exposes_required_metrics():
    get("/health")
    r = get("/metrics")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
    assert "app_info" in body


def test_fault_injection_disabled_returns_404(monkeypatch):
    monkeypatch.delenv("ENABLE_FAULT_INJECTION", raising=False)
    assert get("/simulate-error").status_code == 404


def test_fault_injection_enabled_returns_500(monkeypatch):
    monkeypatch.setenv("ENABLE_FAULT_INJECTION", "true")
    assert get("/simulate-error").status_code == 500
