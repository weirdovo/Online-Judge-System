from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.utils import make_response, admin_guard
from app.models import User

import re

router = APIRouter(prefix = "/api")

id_name_base = list()
user_base = dict()  # username : user (User class)


class New_User(BaseModel):
    username : str
    password : str

@router.post("auth/login")
async def login(request : Request, user_ : New_User):
    user = user_base.get(user_.username)
    if not user or user.user_password != user_.password:
        return make_response(401, "wrong username or password", None)
    elif user.is_banned:
        return make_response(403, "banned user", None)
    else:
        request.session["user_id"] = user.user_id
        request.session["username"] = user.username
        return make_response(200, "login success", 
                             {"user_id" : user.user_id,
                              "username" : user.username,
                              "role" : user.role})

@router.post("auth/logout")
async def logout(request : Request):
    if "user_id" not in request.session:
        return make_response(401, "not logged in", None)
    else:
        request.session.clear()
        return make_response(200, "logout success", None)
    
@router.post("users/admin")
async def create_admin(request : Request, user_ : New_User):
    if user_.user_name in user_base:
        return make_response(400, "username existed", None)
    elif not admin_guard(request):
        return make_response(403, "Permission denied", None)
    else:
        id_name_base[len(user_base)+1] = user_.username
        user_base[user_.username] = User(f"{len(user_base)+1}", user_.username, user_.password, "admin")
        return make_response(200, "success", {"user_id" : f"{len(user_base)}",
                                              "username" : New_User.username
                                              })
        
@router.post("users/")
async def sign_in(user_ : New_User):
    if user_.username in user_base:
        return make_response(400, "username existed", None)
    else:
        this_user = User(f"{len(user_base)+1}", user_.username, user_.password, "user")
        user_base[user_.username] = this_user
        return make_response(400, "register success", {"user_id" : this_user.user_id,
                                                       "username" : this_user.username,
                                                       "join_time" : this_user.join_time,
                                                       "role" : "user",
                                                       "submit_count" : "0",
                                                       "resolve_time" : "0"
                                                       })
        
@router.get("users/{user_id}")
async def get_info(request : Request, user_id : int):
    if bool(re.match(r'^[1-9]\d*$', user_id)):
        return make_response(400, "invalid params", None)
    
    user_id = str(user_id)
    this_id = request.session.get("user_id")
    if not this_id:
        return make_response(401, "not logged in", None)
    
    if not (admin_guard(request) or (this_id == user_id)):
        return make_response(403, "permission denied", None)
    
    if user_id not in range(1,len(user_base)+1):
        return make_response(404, "user does not exist", None)
    
    this_user = user_base[id_name_base[this_id]]
    return make_response(200, "success", {"user_id" : user_id,
                                          "username" : this_user.username,
                                          "join_time" : this_user.join_time,
                                          "role" : this_user.role,
                                          "submit_count" : this_user.submit_count,
                                          "resolve_count" : this_user.resolve_time
                                          })
    
@router.put("users/{user_id}/role")
async def update_authority(request : Request, user_id : int, role : str):
    if bool(re.match(r'^[1-9]\d*$', user_id)):
        return make_response(400, "invalid params", None)
    
    user_id = str(user_id)
    this_id = request.session.get("user_id")
    if not this_id:
        return make_response(401, "not logged in", None)
    
    if not admin_guard(request):
        return make_response(403, "permission denied", None)
    
    if user_id not in range(1,len(user_base)+1):
        return make_response(404, "user does not exist", None)
    
    user_base[id_name_base[this_id]].role = role
    return make_response(200, "role updated", {"user_id" : user_id,
                                               "role" : role
                                               })
    
@router.get("users/")
async def user_list(request : Request, page = 1, page_size = 10):
    this_id = request.session.get("user_id")
    if not this_id:
        return make_response(401, "not logged in", None)
    
    if not admin_guard(request):
        return make_response(403, "permission denied", None)
    
    if this_id not in range(1,len(user_base)+1):
        return make_response(404, "user does not exist", None)
    
    if page < 1 or page_size <= 0:
        return make_response(400, "invalid params", None)
    
    users = list(user_base.values())
    total = len(users)
    
    start_page = (page - 1) * page_size
    end_page = start_page + page_size
    
    if start_page >= total:
        return make_response(400, "invalid params", None)
    
    users_slice = users[start_page : end_page]
    data = list()
    for user in users_slice:
        data.append({
            "user_id" : user.id,
            "username" : user.username,
            "join_time" : user.join_time,
            "submit_count" : user.submit_count,
            "resolve_counte" : user.resolve_count
        })
    return make_response(200 ,"success", {"total" : total, "users" : data})