import random
import smtplib
from typing import Optional, Tuple

from auth.models import User
from auth.utils import get_user_db
from config import SECRET_AUTH
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

HOST = "smtp.gmail.com"
PORT = 587

FROM_EMAIL = "cyberdopc@gmail.com"
PASSWORD = "fewe tcgm diaj feol"


async def generate_random_credentials():
    # Генерация рандомного логина и пароля
    random_login = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7))
    random_password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))
    return random_login, random_password


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        print(f"Email: {user.email}")

        TO_EMAIL = user.email

        random_login, random_password = await generate_random_credentials()
        print(f"Random login: {random_login}")
        print(f"Random password: {random_password}")

        MESSAGE = f"""Subject: Random Credentials

        Your random login: {random_login}
        Your random password: {random_password}
        """

        smtp = smtplib.SMTP(HOST, PORT)
        smtp.starttls()
        smtp.login(FROM_EMAIL, PASSWORD)
        smtp.sendmail(FROM_EMAIL, TO_EMAIL, MESSAGE)
        smtp.quit()

        return random_login, random_password, user

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> Tuple[models.UP, str, str]:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        random_login, random_password, user = await self.on_after_register(user_create,
                                                                           request)  # Получаем сгенерированный логин и пароль из метода on_after_register

        user_dict = (
            user.create_update_dict()
            if safe
            else user.create_update_dict_superuser()
        )
        user_dict["role_id"] = 1
        user_dict["username"] = random_login  # Используем случайный логин в качестве имени пользователя
        user_dict["hashed_password"] = self.password_helper.hash(random_password)  # Используем случайный пароль в качестве хэшированного пароля

        created_user = await self.user_db.create(user_dict)

        return created_user, random_login, random_password


async def get_user_manager(user_db=Depends(get_user_db)):
    return UserManager(user_db)
