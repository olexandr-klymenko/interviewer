from os import environ

CACHE_URL = environ.get("CACHE_URL", "redis://redis")
EXECUTION_TIME_LIMIT = int(environ.get("EXECUTION_TIME_LIMIT", 10))
