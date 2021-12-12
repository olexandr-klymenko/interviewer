from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from interviewer.config import config
from interviewer.constants import AUTH_COOKIE_NAME
from interviewer.routers.user import schemas, services

templates = Jinja2Templates(directory="interviewer/templates")

router = APIRouter(tags=["auth"])


@router.get("/login")
async def google_auth(request: Request):
    return templates.TemplateResponse(
        "auth.html",
        {
            "request": request,
            "GOOGLE_CLIENT_ID": config.get("GOOGLE_CLIENT_ID"),
            "DOMAIN": request.url.hostname,
        },
    )


@router.post("/google/auth", response_model=schemas.User)
async def google_auth(request: Request, user: schemas.User):
    await services.google_auth(user.token)
    response = Response(user.json())
    response.set_cookie(
        AUTH_COOKIE_NAME,
        value=user.token,
        domain=request.url.hostname,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response
