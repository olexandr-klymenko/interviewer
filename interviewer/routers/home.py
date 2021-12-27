from uuid import uuid4

from fastapi import APIRouter, Request

from fastapi.responses import HTMLResponse, RedirectResponse

from interviewer.services.cache import redis
from interviewer.config import (
    config,
    DEFAULT_API_PROTOCOL,
    DEFAULT_DOMAIN,
)
from interviewer.constants import SESSIONS, SESSION_COOKIE_NAME
from interviewer.routers import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if session_id := request.cookies.get(SESSION_COOKIE_NAME):
        if await redis.hexists(SESSIONS, session_id):
            return RedirectResponse(f"/sessions/{session_id}")

    session_id = str(uuid4())
    await redis.hset(SESSIONS, session_id, "")

    page = templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "API_PROTOCOL": config.get("API_PROTOCOL", default=DEFAULT_API_PROTOCOL),
            "DOMAIN": config.get("DOMAIN", default=DEFAULT_DOMAIN),
            "SESSION_ID": session_id,
        },
    )
    page.set_cookie(
        SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return page
