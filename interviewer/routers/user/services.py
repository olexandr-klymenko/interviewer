from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

from interviewer.config import config
from interviewer.routers.user import schemas, models
from interviewer.routers.user import tokenizer


async def create_user(user: schemas.UserCreate) -> models.User:
    _user = await models.User.objects.get_or_create(**user.dict(exclude={"token"}))
    return _user


async def google_auth(user: schemas.UserCreate) -> tuple:
    try:
        id_token.verify_oauth2_token(
            user.token, requests.Request(), config.get("GOOGLE_CLIENT_ID")
        )
    except ValueError:
        raise HTTPException(403, "Bad code")
    user = await create_user(user)
    internal_token = tokenizer.create_token(user.id)
    return user.id, internal_token.get("access_token")
