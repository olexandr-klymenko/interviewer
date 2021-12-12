from pydantic import EmailStr, BaseModel


class User(BaseModel):
    email: EmailStr
    token: str
