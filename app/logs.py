from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas import log_history
from app.models import LogHistory
from app.utils import get_db, make_response, admin_guard

router = APIRouter(prefix = "/api/logs")

@router.get("/access/")
async def log_history(request : Request, lh : log_history = Depends(), db : Session = Depends(get_db)):
    if not lh.valid_params():
        return make_response(400, "invalid params", None)
    if not request.session.get("user_id"):
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)
    
    query = db.query(LogHistory)
    if lh.user_id is not None:
        query = query.filter(LogHistory.user_id == lh.user_id)
    if lh.problem_id is not None:
        query = query.filter(LogHistory.problem_id == lh.problem_id) 
    if lh.page_size is not None:
        offset = (lh.page - 1) * lh.page_size
        query = query.offset(offset).limit(lh.page_size)
        
    history = query.all()
    result = []
    for h in history:
        result.append({"user_id" : h.user_id,
                       "problem_id" : h.problem_id,
                       "action" : "view_log",
                       "time" : h.time,
                       "status" : h.status
                       })
    return make_response(200, "success", result)