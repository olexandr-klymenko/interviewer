from fastapi import Query, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from starlette.responses import Response

from interviewer.cache import redis
from interviewer.config import (
    config,
    DEFAULT_API_PROTOCOL,
    DEFAULT_WS_PROTOCOL,
    DEFAULT_DOMAIN,
)
from interviewer.constants import SESSION_COOKIE_NAME, SESSIONS
from interviewer.execution import execute
from interviewer.routers import templates
from interviewer.sessions import output_sessions

router = APIRouter()


@router.get("/{session_id}/", response_class=HTMLResponse)
async def sessions(request: Request, session_id: str = Query):
    page = templates.TemplateResponse(
        "editor.html",
        context={
            "request": request,
            "API_PROTOCOL": config.get("API_PROTOCOL", default=DEFAULT_API_PROTOCOL),
            "WS_PROTOCOL": config.get("WS_PROTOCOL", default=DEFAULT_WS_PROTOCOL),
            "DOMAIN": config.get("DOMAIN", default=DEFAULT_DOMAIN),
            "SESSION_ID": session_id,
        },
    )

    if session_id != request.cookies.get(SESSION_COOKIE_NAME):
        page.set_cookie(
            SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            max_age=1800,
            expires=1800,
        )

    if await redis.hexists(SESSIONS, session_id):
        return page

    return RedirectResponse("/")


@router.get("/{session_id}/run/")
async def run(session_id: str):
    if await redis.hexists(SESSIONS, session_id):
        code = await redis.hget(SESSIONS, session_id)
        execution_info = execute(session_id=session_id, code=code.encode())
        await output_sessions.broadcast(execution_info.output(), session_id=session_id)
        return Response(status_code=200)
    return Response(status_code=404)


@router.get("/{session_id}/python_version/")
async def python_version(session_id: str):
    execution_info = execute(
        session_id=session_id, code="import sys;print(sys.version)".encode()
    )
    data = f"Python version: {execution_info.output()['output'].split()[0]}"
    return Response(data)
