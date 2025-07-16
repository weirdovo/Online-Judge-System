from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.utils import get_db, make_response, admin_guard
from app.models import User, Problem, Submission

router = APIRouter(prefix="/api/export")


@router.get("/")
async def export_data(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)
    try:
        users = list(db.query(User).all())
        problems = list(db.query(Problem).all())
        submissions = list(db.query(Submission).all())
        data = {}
        data["users"] = [
            {
                "user_id": user.id,
                "username": user.username,
                "password": user.password,
                "role": user.role,
                "join_time": user.join_time,
                "submit_count": user.submit_count,
                "resolve_count": user.resolve_count,
            }
            for user in users
        ]
        data["problems"] = [problem.to_dict() for problem in problems]
        data["submissions"] = [
            {
                "submission_id": sub.id,
                "user_id": sub.user_id,
                "problem_id": sub.problem_id,
                "language": sub.language,
                "code": sub.code,
                "status": sub.status,
                "details": sub.detail,
                "score": sub.score,
                "counts": sub.counts,
            }
            for sub in submissions
        ]
        return make_response(200, "success", data)
    except:
        return make_response(500, "server error", None)
