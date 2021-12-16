from uuid import uuid4

import loguru
from fastapi import APIRouter, Request, HTTPException, Form
import starlette.status as status

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from interviewer.cache import redis
from interviewer.config import config
from interviewer.google_auth import google_auth_verify_token
from interviewer.constants import SESSIONS, SESSION_COOKIE_NAME, AUTH_COOKIE_NAME

router = APIRouter()
templates = Jinja2Templates(directory="interviewer/templates")


@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    if access_token := request.cookies.get(AUTH_COOKIE_NAME):
        try:
            await google_auth_verify_token(access_token)
            loguru.logger.info(f"Logged in with token: {access_token}")
        except HTTPException:
            return RedirectResponse("/")

    if session_id := request.cookies.get(SESSION_COOKIE_NAME):
        if await redis.hexists(SESSIONS, session_id):
            return RedirectResponse(f"/{session_id}")

    session_id = str(uuid4())
    await redis.hset(SESSIONS, session_id, "")

    page = templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "SESSION_ID": session_id,
        },
    )
    page.set_cookie(
        SESSION_COOKIE_NAME,
        value=session_id,
        domain=request.url.hostname,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return page


@router.get("/{session_id}/", response_class=HTMLResponse)
async def editor(request: Request, session_id: str):
    if await redis.hexists(SESSIONS, session_id):
        page = templates.TemplateResponse(
            "editor.html", context={"request": request, "session_id": session_id}
        )
        return page
    return RedirectResponse("/home")


@router.get("/", response_class=HTMLResponse)
async def auth(request: Request):
    if access_token := request.cookies.get(AUTH_COOKIE_NAME):
        await google_auth_verify_token(access_token)
        loguru.logger.info(f"Logged in with token: {access_token}")

    page = templates.TemplateResponse(
        "auth.html",
        context={
            "request": request,
            "GOOGLE_CLIENT_ID": config.get("GOOGLE_CLIENT_ID"),
            "DOMAIN": request.url.hostname,
        },
    )
    return page


@router.post("/google/auth")
async def google_auth(request: Request, credential: str = Form(...)):
    await google_auth_verify_token(credential)
    response = RedirectResponse("/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        AUTH_COOKIE_NAME,
        value=credential,
        domain=request.url.hostname,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response
