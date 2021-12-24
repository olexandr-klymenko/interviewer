from fastapi import Header, APIRouter, Form, Query
from starlette import status as status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from interviewer.config import config, DEFAULT_API_PROTOCOL, DEFAULT_DOMAIN
from interviewer.constants import AUTH_COOKIE_NAME
from interviewer.auth import google_auth_verify_token
from interviewer.routers import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def auth(request: Request, referer: str = Query("/")):
    page = templates.TemplateResponse(
        "auth.html",
        context={
            "request": request,
            "GOOGLE_CLIENT_ID": config.get("GOOGLE_CLIENT_ID"),
            "API_PROTOCOL": config.get("API_PROTOCOL", default=DEFAULT_API_PROTOCOL),
            "DOMAIN": config.get("DOMAIN", default=DEFAULT_DOMAIN),
            "REFERER": referer,
        },
    )
    return page


@router.post("/")
async def google_auth(credential: str = Form(...), referer: str = Query(default="/")):
    await google_auth_verify_token(credential)
    response = RedirectResponse(referer, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        AUTH_COOKIE_NAME,
        value=credential,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response
