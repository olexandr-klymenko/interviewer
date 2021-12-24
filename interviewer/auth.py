import loguru
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

from interviewer.config import config


async def google_auth_verify_token(oauth2_token: str):
    try:
        id_token.verify_oauth2_token(
            oauth2_token, requests.Request(), config.get("GOOGLE_CLIENT_ID")
        )
    except ValueError:
        raise HTTPException(403, "Bad code")


async def is_authenticated(access_token):
    if access_token:
        try:
            await google_auth_verify_token(access_token)
            loguru.logger.info(f"Logged in with token: {access_token}")
            return True
        except HTTPException:
            return False
    else:
        return False
