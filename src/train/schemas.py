from typing import Optional

from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    id: int
    Exercises: str
    Timer: int
    Repetitions: int


class ExerciseUpdate(BaseModel):
    timer: Optional[int] = Field(None)
    repetitions: Optional[int] = Field(None)
