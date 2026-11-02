import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

app = Flask(__name__)

VERSION = os.environ.get("APP_VERSION", "2.0.0")


def get_environment():
    # ENVIRONMENT is the Mini Project 2 name; APP_ENV still works as a fallback.
    return os.environ.get("APP_ENV", "unknown")


# ---- Metrics ----
REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)
APP_INFO = Gauge("app_info", "Application info", ["version", "environment"])
APP_INFO.labels(version=VERSION, environment=get_environment()).set(1)


# ---- Structured JSON logging to stdout ----
class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))
        return json.dumps(entry)


logger = logging.getLogger("system-health")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(JsonFormatter())
logger.handlers = [_handler]
logger.propagate = False


@app.before_request
def start_timer():
    g.start_time = time.perf_counter()


@app.after_request
def record_request(response):
    duration = time.perf_counter() - g.get("start_time", time.perf_counter())
    # Metrics use the route pattern (low cardinality); logs use the real path.
    metric_endpoint = request.url_rule.rule if request.url_rule else "unmatched"
    REQUESTS.labels(request.method, metric_endpoint, str(response.status_code)).inc()
    LATENCY.labels(metric_endpoint).observe(duration)

    failed = response.status_code >= 500
    logger.log(
        logging.ERROR if failed else logging.INFO,
        "request failed" if failed else "request completed",
        extra={
            "fields": {
                "endpoint": request.path,
                "method": request.method,
                "status": response.status_code,
                "environment": get_environment(),
            }
        },
    )
    return response


# ---- Endpoints ----
@app.route("/health")
def health():
    return jsonify(status="UP")


@app.route("/version")
def version():
    return jsonify(version=VERSION)


@app.route("/environment")
def environment():
    return jsonify(environment=get_environment())


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.route("/simulate-error")
def simulate_error():
    if os.environ.get("ENABLE_FAULT_INJECTION", "false").lower() != "true":
        return jsonify(error="not found"), 404
    return jsonify(error="simulated failure"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
