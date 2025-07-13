from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime

def make_response(code, msg, data):
    return JSONResponse(status_code = code, content = {
                        "code" : code,
                        "msg" : msg,
                        "data" : data
                        })
    
def get_time():    
    now = datetime.now()
    return now.strftime("%Y-%m-%d")
    
def get_role(request : Request):
    from app.authorization import user_base   # break circular import
    name = request.session.get("username")   
    if not name:
        return "guest"
    else:
        return user_base[name].role
    
def admin_guard(request : Request):
    if get_role(request) == "admin":
        return True
    return False
    
    