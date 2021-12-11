import aioredis
import loguru
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from interviewer.routers.user.login import router as login_router
from interviewer.routers.execution import router as execution_router
from interviewer.routers.views import router as views_router
from interviewer.routers.web_sockets import router as websockets_router
from interviewer.cache import redis
from interviewer.db import database, metadata, engine


app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="secret-string")
app.mount("/static", StaticFiles(directory="interviewer/static"), name="static")
app.include_router(login_router)
app.include_router(execution_router)
app.include_router(views_router)
app.include_router(websockets_router)

metadata.create_all(engine)
app.state.database = database


@app.on_event("startup")
async def check_redis():
    try:
        await redis.ping()
    except aioredis.exceptions.ConnectionError as err:
        loguru.logger.error(err)
        raise


@app.on_event("startup")
async def connect_database() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def disconnect_database() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


if __name__ == "__main__":
    # TODO: Remove code below as soon as PyCharm FastAPI run configuration in debug mode resolved
    import uvicorn

    uvicorn.Server(uvicorn.Config(app=app)).run()
