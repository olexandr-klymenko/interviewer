from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from interviewer.routers.login import router as login_router
from interviewer.routers.execution import router as execution_router
from interviewer.routers.views import router as views_router
from interviewer.routers.web_sockets import router as websockets_router


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
