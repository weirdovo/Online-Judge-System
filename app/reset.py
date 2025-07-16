from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.utils import make_response, admin_guard, get_db
from app.models import Submission, Problem, User, Language, LogHistory
import bcrypt
router = APIRouter(prefix="/api")

@router.post("/reset/")
async def reset_system(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)

    db.query(Submission).delete()
    db.query(Problem).delete()
    db.query(Language).delete()
    db.query(User).delete()
    db.query(LogHistory).delete()
    admin = User(username = "admin", 
                 password = bcrypt.hashpw("admintestpassword".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 
                 role = "admin") 
    
    python = Language(name="python", file_ext=".py", run_cmd="python3 {src}")
    db.add_all([admin, python])
    db.commit()
    
    return make_response(200, "system reset successfully", None)