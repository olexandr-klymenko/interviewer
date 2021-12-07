from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from interviewer.routers.api import router as api_router
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
app.mount("/static", StaticFiles(directory="interviewer/static"), name="static")
app.include_router(api_router)
app.include_router(views_router)
app.include_router(websockets_router)
