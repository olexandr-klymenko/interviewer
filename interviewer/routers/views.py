from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from interviewer.cache import redis
from interviewer.constants import SESSIONS

router = APIRouter()
templates = Jinja2Templates(directory="interviewer/templates")


SESSION_COOKIE_NAME = "live_coding_session"


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if session_id := request.cookies.get(SESSION_COOKIE_NAME):
        if await redis.hexists(SESSIONS, session_id):
            return RedirectResponse(f"/{session_id}")

    session_id = str(uuid4())
    await redis.hset(SESSIONS, session_id, "")
    page = templates.TemplateResponse(
        "index.html", context={"request": request, "session_id": session_id}
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
    return RedirectResponse("/")
