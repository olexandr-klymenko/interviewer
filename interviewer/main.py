import os
from dataclasses import dataclass
import subprocess
from collections import defaultdict
from tempfile import NamedTemporaryFile
from uuid import uuid4
from time import time
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket, WebSocketDisconnect

from aioredis import from_url

SESSIONS = "SESSIONS"
EXECUTION_TIME_LIMIT = 10


class Sessions:
    def __init__(self):
        self._info: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)

    def add(self, session_id, socket_id, socket):
        self._info[session_id].update({socket_id: socket})

    async def echo(self, data, session_id, source_socket_id=None):
        for socket in self._target_sockets(
            session_id=session_id, source_socket_id=source_socket_id
        ):
            if isinstance(data, str):
                await socket.send_text(data)
            if isinstance(data, dict):
                await socket.send_json(data)

    def _target_sockets(self, session_id, source_socket_id=None) -> List[WebSocket]:
        return [
            socket
            for _id, socket in self._info[session_id].items()
            if _id != source_socket_id
        ]

    def remove_socket(self, session_id, socket_id):
        self._info[session_id].pop(socket_id)


editor_sessions = Sessions()
output_sessions = Sessions()


redis = from_url("redis://redis", encoding="utf-8", decode_responses=True)

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@dataclass
class ExecuteData:
    stdout: str
    stderr: str
    execution_time: float = 0.0

    def output(self) -> Dict[str, float]:
        return {"output": self.stdout or self.stderr, "time": self.execution_time}


def execute(session_id: str, code: bytes) -> ExecuteData:
    tmp_file = NamedTemporaryFile(prefix=session_id, delete=False)
    try:
        tmp_file.write(code)
        tmp_file.close()
        start_time = time()
        completed = subprocess.run(
            ["python3", tmp_file.name],
            capture_output=True,
            timeout=EXECUTION_TIME_LIMIT,
        )
        return ExecuteData(
            stdout=completed.stdout.decode(),
            stderr=completed.stderr.decode(),
            execution_time=time() - start_time,
        )
    except (subprocess.TimeoutExpired, Exception) as err:
        return ExecuteData(stdout="", stderr=str(err))
    finally:
        os.unlink(tmp_file.name)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_id = str(uuid4())
    await redis.hset(SESSIONS, session_id, "")
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


@app.get("/run/{session_id}")
async def run(session_id: str):
    if await redis.hexists(SESSIONS, session_id):
        code = await redis.hget(SESSIONS, session_id)
        execution_info = execute(session_id=session_id, code=code.encode())
        await output_sessions.echo(execution_info.output(), session_id=session_id)
        return Response(status_code=200)
    return Response(status_code=404)


@app.websocket("/editor_ws/{session_id}")
async def editor_web_socket(websocket: WebSocket, session_id: str):
    socket_id = str(uuid4())
    editor_sessions.add(session_id=session_id, socket_id=socket_id, socket=websocket)
    await websocket.accept()
    text = await redis.hget(SESSIONS, session_id)
    await websocket.send_text(text)
    try:
        while True:
            data = await websocket.receive_text()
            await redis.hset(SESSIONS, session_id, data)
            await editor_sessions.echo(
                session_id=session_id,
                source_socket_id=socket_id,
                data=data,
            )

    except WebSocketDisconnect:
        editor_sessions.remove_socket(session_id=session_id, socket_id=socket_id)


@app.websocket("/output_ws/{session_id}")
async def output_web_socket(websocket: WebSocket, session_id: str):
    socket_id = str(uuid4())
    output_sessions.add(session_id=session_id, socket_id=socket_id, socket=websocket)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await output_sessions.echo(
                session_id=session_id,
                source_socket_id=socket_id,
                data=data,
            )

    except WebSocketDisconnect:
        output_sessions.remove_socket(session_id=session_id, socket_id=socket_id)


if __name__ == "__main__":
    redis = from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    uvicorn.run(app)
