from fastapi import FastAPI, Request, Depends
from starlette.middleware.sessions import SessionMiddleware
from app import problems, users, submissions, languages
from app.models import User, Language
from app.problems import make_response
from app.db import engine, Base
from app.utils import get_db
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

Base.metadata.create_all(bind = engine) #

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    exist_admin = db.query(User).filter_by(username = "admin").first()
    exist_python = db.query(Language).filter_by(name = "python").first()
    if not exist_admin:
        admin = User(username = "admin", password = "admintestpassword", role = "admin")  # Create administrator
        db.add(admin)
        db.commit()
        db.refresh(admin)
    if not exist_python:
        python = Language(name = "python", file_ext = ".py", run_cmd = "python3 {src}",)  # Create python
        db.add(python)
        db.commit()
        db.refresh(python)
    yield

app = FastAPI(
    title = "Simple OJ System - Student Template",
    description = "A simple online judge system for programming assignments",
    version = "1.0.0",
    lifespan = lifespan
)
app.add_middleware(SessionMiddleware, secret_key = "add_a_real_secret_key_later") # add secret-key

app.include_router(problems.router)
app.include_router(users.router)
app.include_router(submissions.router)
app.include_router(languages.router)

@app.get("/")
async def welcome():
    return "Welcome!"

# handle different kinds of exceptions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    path = str(request.url.path)
    if "/problems" in path:
        msg = "invalid format"
    elif "/login" in path:
        msg = "invalid params"
    elif "/admin" in path:
        msg = "invalid params"
    elif "/users" in path:
        msg = "invalid params"
    elif "/submissions" in path:
        msg = "invalid params"
    elif "/languages" in path:
        msg = "invalid params"
    return make_response(400, msg, None)    