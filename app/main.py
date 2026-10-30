"""Small config service for the DevOps assessment.

Implemented with Claude Code (model: Claude Opus 5.5, effort: low),
reviewed by the repository author.

Endpoints:
    GET    /health          liveness/readiness check
    GET    /version         application version
    GET    /env             value of the ENVIRONMENT variable
    POST   /config          create or overwrite a config entry
    GET    /config/<name>   read a config entry
    DELETE /config/<name>   delete a config entry

Config entries live in process memory, so they are lost on restart and are
not shared between processes or pods. Run a single worker process
(threads are fine) to keep behaviour consistent.
"""

import os
import re
import threading

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

DEFAULT_VERSION = "1.0.0"

# Names end up in the URL path, so keep them URL-safe and bounded.
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
MAX_VALUE_LENGTH = 4096


class ConfigStore:
    """Thread-safe in-memory key/value store."""

    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def set(self, name, value):
        with self._lock:
            self._data[name] = value

    def get(self, name):
        with self._lock:
            return self._data.get(name)

    def delete(self, name):
        with self._lock:
            return self._data.pop(name, None) is not None


def create_app(store=None):
    app = Flask(__name__)
    app.json.sort_keys = False
    store = store if store is not None else ConfigStore()

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        # Return JSON instead of Flask's default HTML error pages.
        return jsonify(error=err.description), err.code

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/version")
    def version():
        return jsonify(version=os.environ.get("APP_VERSION", DEFAULT_VERSION))

    @app.get("/env")
    def env():
        # Read on every request so the value always matches the process env.
        return jsonify(environment=os.environ.get("ENVIRONMENT", "unknown"))

    @app.post("/config")
    def create_config():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="request body must be a JSON object"), 400

        name = body.get("name")
        value = body.get("value")

        if not isinstance(name, str) or not NAME_PATTERN.match(name):
            return jsonify(
                error="'name' must be 1-128 characters of letters, digits, '_', '.' or '-'"
            ), 400
        if not isinstance(value, str):
            return jsonify(error="'value' must be a string"), 400
        if len(value) > MAX_VALUE_LENGTH:
            return jsonify(error=f"'value' must be at most {MAX_VALUE_LENGTH} characters"), 400

        store.set(name, value)
        return jsonify(name=name, value=value), 201

    @app.get("/config/<name>")
    def get_config(name):
        value = store.get(name)
        if value is None:
            return jsonify(error=f"config '{name}' not found"), 404
        return jsonify(name=name, value=value)

    @app.delete("/config/<name>")
    def delete_config(name):
        if not store.delete(name):
            return jsonify(deleted=False), 404
        return jsonify(deleted=True)

    return app


app = create_app()


if __name__ == "__main__":
    # Local development only; use gunicorn in containers.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
