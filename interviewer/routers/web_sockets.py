from uuid import uuid4

from fastapi import WebSocketDisconnect, WebSocket, APIRouter
from loguru import logger

from interviewer.services.cache import redis
from interviewer.constants import SESSIONS
from interviewer.services.sessions import editor_sessions, output_sessions


router = APIRouter()


@router.websocket("/editor")
async def editor_web_socket(websocket: WebSocket, session_id: str):
    socket_id = str(uuid4())
    await editor_sessions.connect(
        session_id=session_id, socket_id=socket_id, socket=websocket
    )
    text = await redis.hget(SESSIONS, session_id)
    await websocket.send_text(text)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            await redis.hset(SESSIONS, session_id, data)
            await editor_sessions.broadcast(
                session_id=session_id,
                source_socket_id=socket_id,
                data=data,
            )

    except WebSocketDisconnect:
        editor_sessions.disconnect(session_id=session_id, socket_id=socket_id)


@router.websocket("/output")
async def output_web_socket(websocket: WebSocket, session_id: str):
    socket_id = str(uuid4())
    await output_sessions.connect(
        session_id=session_id, socket_id=socket_id, socket=websocket
    )
    try:
        while True:
            data = await websocket.receive_text()
            await output_sessions.broadcast(
                session_id=session_id,
                source_socket_id=socket_id,
                data=data,
            )

    except WebSocketDisconnect:
        output_sessions.disconnect(session_id=session_id, socket_id=socket_id)
