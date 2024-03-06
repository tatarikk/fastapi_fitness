from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: Optional[int]
    email: Optional[str]
    username: Optional[str]
    role_id: Optional[int]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    id: Optional[int]
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]
    role_id: Optional[int]
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False