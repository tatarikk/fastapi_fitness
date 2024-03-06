from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from train.models import exercises
from fastapi.responses import JSONResponse
from train.schemas import ExerciseUpdate

router = APIRouter(
    prefix="/exercises",
    tags=["Exercises"]
)

exercises_data = [
    {"Timer": 60, "Exercises": "High Knees", "Repetitions": 15},
    {"Timer": 60, "Exercises": "Jumping Jacks", "Repetitions": 15},
]


@router.get("/getexer")
async def get_exercises(session: AsyncSession = Depends(get_async_session)):
    query = select(exercises)
    result = await session.execute(query)
    exercise = result.fetchall()

    if not exercise:
        raise HTTPException(status_code=404, detail="Operations not found")

    # Преобразуем каждую операцию в словарь
    exercises_data = [{"Timer": op.Timer, "Exercises": op.Exercise, "Repetitions": op.Repetitions}
                      for op in exercise]
    print(exercises_data)

    return exercises_data


@router.get("/all_exercises")
async def get_exercises_without_db():
    return exercises_data


@router.put("/all_exercises/{index}")
async def edit_exercise(index: int, exercise_update: ExerciseUpdate):
    if 0 <= index < len(exercises_data):
        exercises_data[index]["Timer"] = exercise_update.timer
        exercises_data[index]["Repetitions"] = exercise_update.repetitions
        return {"message": "Exercise data updated successfully"}
    else:
        return {"error": "Index out of range"}
