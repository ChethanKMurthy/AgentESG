"""Production Gunicorn config for uvicorn workers.

Tunables read from env so the same image works across ECS task sizes.
"""
from __future__ import annotations

import multiprocessing
import os


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


# Bind
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")

# Workers: (2 * CPUs) + 1 by default, override via env
_default_workers = multiprocessing.cpu_count() * 2 + 1
workers = _int_env("GUNICORN_WORKERS", _default_workers)
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = _int_env("GUNICORN_TIMEOUT", 120)
graceful_timeout = _int_env("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _int_env("GUNICORN_KEEPALIVE", 5)

# Logging
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = (
    '%({x-request-id}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(D)s'
)

# Hygiene
max_requests = _int_env("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = _int_env("GUNICORN_MAX_REQUESTS_JITTER", 100)
preload_app = os.environ.get("GUNICORN_PRELOAD", "false").lower() == "true"
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "*")
proxy_allow_ips = os.environ.get("PROXY_ALLOW_IPS", "*")
