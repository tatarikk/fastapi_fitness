from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from operations.router import get_specific_operations
from train.router import get_exercises

router = APIRouter(
    tags=["Pages"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/auth/register")
def get_reg_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@router.get("/auth/login")
def get_log_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/operations/getinfo")
def get_search_page(request: Request, operations=Depends(get_specific_operations)):
    return templates.TemplateResponse("get_info.html", {"request": request, "operations": operations})


@router.get("/operations/addinfo")
def add_search_page(request: Request):
    return templates.TemplateResponse("addinfo.html", {"request": request})


@router.get("/exercises/getexer")
def get_ex_page(request: Request, exercises: list = Depends(get_exercises)):
    return templates.TemplateResponse("get_exer.html", {"request": request, "exercise": exercises})


# all_exercises

@router.get("/exercises/all_exercises")
def get_all_ex(request: Request, exercises: list = Depends(get_exercises)):
    return templates.TemplateResponse("all_exercises.html", {"request": request, "exercise": exercises})


@router.get("/auth/pre_registration")
def pre_registration_page(request: Request):
    return templates.TemplateResponse("pre_registration.html", {"request": request})
