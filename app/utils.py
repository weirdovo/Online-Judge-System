from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from app.db import Localsession
from app.schemas import New_User


def make_response(code, msg, data):
    return JSONResponse(
        status_code=code, content={"code": code, "msg": msg, "data": data}
    )


def get_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


def get_db():
    db = Localsession()
    try:
        yield db
    finally:
        db.close()


def admin_guard(request: Request):
    name = request.session.get("role")
    if name == "admin":
        return False
    return True


def newuser_validation(user: New_User):
    if len(user.username) >= 3 and len(user.username) <= 40 and len(user.password) >= 6:
        return True
    return False
