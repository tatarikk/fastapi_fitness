from auth.base_config import fastapi_users
from auth.models import User
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException
from operations.models import operation
from operations.schemas import OperationCreate
from auth.models import user
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/operations",
    tags=["User Info"]
)


@router.get("/getinfo")
async def get_specific_operations(session: AsyncSession = Depends(get_async_session)):
    # Выполняем запрос к базе данных, выбирая только операции с определенным пользователем
    query = select(operation).where(operation.c.id == 1)
    result = await session.execute(query)
    operations = result.fetchall()

    if not operations:
        raise HTTPException(status_code=404, detail="Operations not found")

    # Преобразуем каждую операцию в словарь
    operations_data = [
        {"id": op.id, "Name": op.Name, "Surname": op.Surname, "Birthday": op.Birthday, "Gender": op.Gender,
         "Weight": op.Weight, "Height": op.Height, "Activity": op.Activity} for op in operations]

    return operations_data


@router.post("/addinfo")
async def add_specific_operations(new_operation: OperationCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(operation).values(
        Name=new_operation.Name,
        Surname=new_operation.Surname,
        Birthday=new_operation.Birthday,
        Gender=new_operation.Gender,
        Height=new_operation.Height,
        Weight=new_operation.Weight,
        Activity=new_operation.Activity
    )
    await session.execute(stmt)
    await session.commit()
    return {"status": "success"}  # Вбивает данные
