from uuid import uuid4

import loguru
from fastapi import APIRouter, Request, HTTPException

from fastapi.responses import HTMLResponse, RedirectResponse

from interviewer.cache import redis
from interviewer.config import (
    config,
    DEFAULT_API_PROTOCOL,
    DEFAULT_DOMAIN,
)
from interviewer.google_auth import google_auth_verify_token
from interviewer.constants import SESSIONS, SESSION_COOKIE_NAME, AUTH_COOKIE_NAME
from interviewer.routers import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if access_token := request.cookies.get(AUTH_COOKIE_NAME):
        try:
            await google_auth_verify_token(access_token)
            loguru.logger.info(f"Logged in with token: {access_token}")
        except HTTPException:
            return RedirectResponse(f"/auth")
    else:
        return RedirectResponse(f"/auth")

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
