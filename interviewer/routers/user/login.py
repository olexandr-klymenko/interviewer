from fastapi import APIRouter
from starlette.config import Config
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from interviewer.routers.user import schemas, services

config = Config("interviewer/.env")

templates = Jinja2Templates(directory="interviewer/templates")

router = APIRouter(tags=["auth"])


@router.get("/login")
async def google_auth(request: Request):
    return templates.TemplateResponse(
        "auth.html",
        {"request": request, "GOOGLE_CLIENT_ID": config.get("GOOGLE_CLIENT_ID"), "DOMAIN": request.url.hostname},
    )


@router.post("/google/auth", response_model=schemas.Token)
async def google_auth(user: schemas.UserCreate):
    user_id, token = await services.google_auth(user)
    return schemas.Token(id=user_id, token=token)
