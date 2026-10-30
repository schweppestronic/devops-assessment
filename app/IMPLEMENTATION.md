# Implementation

Python 3.12+ with Flask, served by gunicorn. Code is in `main.py`, tests in `tests/`.
Implemented with Claude Code (model: Claude Opus 5.5, effort: low).

## Run locally

```bash
cd app
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt

pytest                                                         # run tests
ENVIRONMENT=dev gunicorn -b 0.0.0.0:8080 -w 1 --threads 4 main:app
```

## Configuration

| Variable      | Default   | Purpose                        |
|---------------|-----------|--------------------------------|
| `ENVIRONMENT` | `unknown` | Returned by `GET /env`         |
| `APP_VERSION` | `1.0.0`   | Returned by `GET /version`     |
| `PORT`        | `8080`    | Port for `python main.py` only |

## Behaviour notes

- `POST /config` returns `201`. Posting an existing name overwrites it.
- `name` must match `[A-Za-z0-9_.-]{1,128}` (it is used in the URL path); `value` must be a string of up to 4096 characters. Invalid input returns `400`.
- `GET`/`DELETE` on a missing name return `404` (`DELETE` returns `{"deleted": false}`).
- All errors are JSON: `{"error": "..."}`.
- Config is stored **in memory**: it is lost on restart and not shared between pods or gunicorn workers. Keep `-w 1` (threads are safe) and `replicaCount: 1`, or move to a shared store (Redis, a database) to scale out.
