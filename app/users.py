from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils import make_response, admin_guard, get_db, newuser_validation
from app.models import User
from app.schemas import New_User, Role

router = APIRouter(prefix = "/api")

@router.post("/auth/login")
async def login(request : Request, user_ : New_User, db : Session = Depends(get_db)):
    user = db.query(User).filter_by(username = user_.username).first()
    if not user or user.password != user_.password:
        return make_response(401, "wrong username or password", None)
    
    if user.is_banned:
        return make_response(403, "banned user", None)
    
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    
    return make_response(200, "login success", 
                            {"user_id" : user.id,
                            "username" : user.username,
                            "role" : user.role})

@router.post("/auth/logout")
async def logout(request : Request):
    if "user_id" not in request.session:
        return make_response(401, "not logged in", None)
    
    request.session.clear()
    return make_response(200, "logout success", None)
    
@router.post("/users/admin")
async def create_admin(request : Request, user_ : New_User, db : Session = Depends(get_db)):

    if not newuser_validation(user_):
        return make_response(400, "invalid username or password", None) 

    if admin_guard(request):
        return make_response(403, "Permission denied", None)
    
    new_admin = User(username = user_.username, password = user_.password, role = "admin")
    db.add(new_admin)
    try :
        db.commit()
        db.refresh(new_admin)
        return make_response(200, "success", {"user_id" : new_admin.id,
                                              "username" : new_admin.username
                                              })
    except IntegrityError:
        db.rollback()
        return make_response(400, "username existed", None)
    
        
@router.post("/users/")
async def sign_in(user_ : New_User, db : Session = Depends(get_db)):
    if not newuser_validation(user_):
        return make_response(400, "invalid username or password", None) 
    new_user = User(username = user_.username, password = user_.password)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return make_response(200, "register success", {"user_id" : new_user.id,
                                                       "username" : new_user.username,
                                                       "join_time" : new_user.join_time,
                                                       "role" : "user",
                                                       "submit_count" : 0,
                                                       "resolve_count" : 0
                                                       })
    except IntegrityError:
        db.rollback()
        return make_response(400, "username existed", None)
      
@router.get("/users/{user_id}")
async def get_info(request : Request, user_id : int, db : Session = Depends(get_db)):
    if not str(user_id).isdigit():
        return make_response(400, "invalid params", None)
    user_id = str(user_id)
    this_id = request.session.get("user_id")
    if not this_id:
        return make_response(401, "not logged in", None)
    if admin_guard(request) and this_id != user_id:
        return make_response(403, "permission denied", None)
    this_user = db.query(User).filter_by(id = user_id).first()
    if not this_user:
        return make_response(404, "user does not exist", None)
    return make_response(200, "success", {"user_id" : this_user.id,
                                          "username" : this_user.username,
                                          "join_time" : this_user.join_time,
                                          "role" : this_user.role,
                                          "submit_count" : this_user.submit_count,
                                          "resolve_count" : this_user.resolve_count
                                          })
    
@router.put("/users/{user_id}/role")
async def update_authority(request : Request, user_id : int, role_ : Role, db : Session = Depends(get_db)):
    role = role_.role
    this_role = request.session.get("role")
    if not this_role:
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)
    user = db.query(User).filter_by(id = user_id).first()
    if not user:
        return make_response(404, "user does not exist", None)
    if role == "banned":
        user.is_banned = True
    elif role == "admin" or role == "user":
        user.role = role
    else:
        return make_response(400, "invalid params", None)
    db.commit()
    return make_response(200, "role updated", {"user_id" : user_id,
                                               "role" : role
                                               })
    
@router.get("/users/")
async def user_list(request : Request, page = 1, page_size = 10, db : Session = Depends(get_db)):
    this_id = request.session.get("user_id")
    if not this_id:
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)
    if page < 1 or page_size <= 0:
        return make_response(400, "invalid params", None)
    users = list(db.query(User).all())
    total = len(users)
    start_page = (page - 1) * page_size
    end_page = start_page + page_size
    if start_page >= total:
        return make_response(400, "invalid params", None)
    users_slice = users[start_page : end_page]
    data = [{
            "user_id" : user.id,
            "username" : user.username,
            "join_time" : user.join_time,
            "submit_count" : user.submit_count,
            "resolve_count" : user.resolve_count
        } for user in users_slice]
    return make_response(200 ,"success", {"total" : total, "users" : data})