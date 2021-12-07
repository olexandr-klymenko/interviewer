from aioredis import from_url

from interviewer.config import CACHE_URL

redis = from_url(CACHE_URL, encoding="utf-8", decode_responses=True)
