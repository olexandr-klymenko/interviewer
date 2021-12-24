import aioredis
import loguru
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from interviewer.auth import is_authenticated
from interviewer.cache import redis
from interviewer.config import (
    config,
    DEFAULT_DOMAIN,
)
from interviewer.constants import AUTH_COOKIE_NAME
from interviewer.routers.auth import router as auth_router
from interviewer.routers.home import router as views_router
from interviewer.routers.sessions import router as sessions_router
from interviewer.routers.web_sockets import router as websockets_router

DOMAIN = config.get("DOMAIN", default=DEFAULT_DOMAIN)

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[DOMAIN, f"*.{DOMAIN}", "localhost", "127.0.0.1"],
)
app.add_middleware(SessionMiddleware, secret_key="secret-string")
app.mount("/static", StaticFiles(directory="interviewer/static"), name="static")
app.include_router(views_router)
app.include_router(sessions_router, prefix="/sessions")
app.include_router(auth_router, prefix="/auth")
app.include_router(websockets_router, prefix="/ws")


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path not in ["/auth/"]:
        if not await is_authenticated(request.cookies.get(AUTH_COOKIE_NAME)):
            return RedirectResponse(f"/auth/?referer={request.url.path}")

    return await call_next(request)


@app.on_event("startup")
async def check_redis():
    try:
        await redis.ping()
    except aioredis.exceptions.ConnectionError as err:
        loguru.logger.error(err)
        raise


if __name__ == "__main__":
    # TODO: Remove code below as soon as PyCharm FastAPI run configuration in debug mode resolved
    import uvicorn

    uvicorn.Server(uvicorn.Config(app=app)).run()
