import os
from flask import Flask, jsonify
app = Flask(__name__)

VERSION = os.environ.get("APP_VERSION", "1.0.0")


@app.route("/health")
def health():
    return jsonify(status="UP")


@app.route("/version")
def version():
    return jsonify(version=VERSION)


@app.route("/environment")
def environment():
    return jsonify(environment=os.environ.get("APP_ENV", "unknown"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
