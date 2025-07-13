from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from app import problems, authorization
from app.models import User
from app.problems import make_response
from app.authorization import user_database
from fastapi.exceptions import RequestValidationError


app = FastAPI(
    title="Simple OJ System - Student Template",
    description="A simple online judge system for programming assignments",
    version="1.0.0"
)
app.add_middleware(SessionMiddleware) # add secret-key

app.include_router(problems.router)
app.include_router(authorization.router)


@app.get("/")
async def welcome():
    user_database["admin"] = User("0", "admin", "admin", "admin")    # Create administrator
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
    return make_response(400, msg, None)    