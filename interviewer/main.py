from collections import defaultdict
from uuid import uuid4
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect
from loguru import logger

from aioredis import from_url

SESSIONS = "SESSIONS_"


class WebSocketSessions:
    def __init__(self):
        self._info: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)

    def add(self, session_id, socket_id, socket):
        self._info[session_id].update({socket_id: socket})

    def sockets_by_session(self, session_id, socket_id) -> List[WebSocket]:
        return [
            socket for _id, socket in self._info[session_id].items() if _id != socket_id
        ]

    def sockets(self, session_id):
        return list(self._info[session_id].keys())

    def remove_socket(self, session_id, socket_id):
        self._info[session_id].pop(socket_id)


web_socket_sessions = WebSocketSessions()


redis = from_url("redis://localhost", encoding="utf-8", decode_responses=True)

app = FastAPI(debug=True)
origins = [
    "http://localhost",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_id = str(uuid4())
    res = await redis.hset(SESSIONS, session_id, "")
    logger.info(res)
    page = templates.TemplateResponse(
        "index.html", context={"request": request, "session_id": session_id}
    )
    return page


@app.get("/{session_id}/", response_class=HTMLResponse)
async def editor(request: Request, session_id: str):
    if await redis.hexists(SESSIONS, session_id):
        page = templates.TemplateResponse(
            "editor.html", context={"request": request, "session_id": session_id}
        )
        return page
    return RedirectResponse("/")


@app.websocket("/editor_ws/{session_id}")
async def editor_web_socket(websocket: WebSocket, session_id: str):
    socket_id = str(uuid4())
    web_socket_sessions.add(
        session_id=session_id, socket_id=socket_id, socket=websocket
    )
    await websocket.accept()
    text = await redis.hget(SESSIONS, session_id)
    await websocket.send_text(text)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            logger.info(web_socket_sessions.sockets(session_id=session_id))
            for socket in web_socket_sessions.sockets_by_session(
                session_id=session_id, socket_id=socket_id
            ):
                await socket.send_text(data)
    except WebSocketDisconnect:
        web_socket_sessions.remove_socket(session_id=session_id, socket_id=socket_id)


if __name__ == "__main__":
    uvicorn.run(app)
