from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from interviewer.cache import redis
from interviewer.constants import SESSIONS

router = APIRouter()
templates = Jinja2Templates(directory="interviewer/templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    session_id = str(uuid4())
    await redis.hset(SESSIONS, session_id, "")
    page = templates.TemplateResponse(
        "index.html", context={"request": request, "session_id": session_id}
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
