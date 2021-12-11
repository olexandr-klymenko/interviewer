from os import environ

from starlette.config import Config

CACHE_URL = environ.get("CACHE_URL", "redis://redis")
EXECUTION_TIME_LIMIT = int(environ.get("EXECUTION_TIME_LIMIT", 10))

config = Config("interviewer/.env")
