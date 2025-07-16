from fastapi import APIRouter, UploadFile, File, Request, Depends
from sqlalchemy.orm import Session
from app.utils import make_response, get_db, admin_guard
from app.models import User, Problem, Submission
import json

router = APIRouter(prefix="/api/import")


@router.post("/")
async def import_data(
    request: Request, file: UploadFile = File(), db: Session = Depends(get_db)
):
    if "user_id" not in request.session:
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)

    if not file.filename.endswith(".json"):
        return make_response(400, "only JSON files", None)

    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        for key in ["users", "problems", "submissions"]:
            if key not in data or not isinstance(data[key], list):
                return make_response(400, f"missing or invalid '{key}'", None)
        for u in data["users"]:
            user = User(
                id=u.get("user_id"),
                username=u["username"],
                password=u["password"],  # already hashed
                role=u.get("role", "user"),
                join_time=u.get("join_time"),
                submit_count=u.get("submit_count", 0),
                resolve_count=u.get("resolve_count", 0),
                is_banned=u.get("is_banned", False),
            )
            db.merge(user)
        for p in data["problems"]:
            problem = Problem(
                id=p["id"],
                title=p["title"],
                description=p["description"],
                input_description=p["input_description"],
                output_description=p["output_description"],
                samples=p["samples"],
                constraints=p["constraints"],
                testcases=p["testcases"],
                hint=p.get("hint", ""),
                source=p.get("source", ""),
                tags=p.get("tags", []),
                time_limit=p.get("time_limit", 1.0),
                memory_limit=p.get("memory_limit", 128),
                author=p.get("author", ""),
                difficulty=p.get("difficulty", ""),
                public_cases=p.get("public_cases", True),
            )
            db.merge(problem)
        for s in data["submissions"]:
            submission = Submission(
                id=s["submission_id"],
                user_id=s["user_id"],
                problem_id=s["problem_id"],
                language=s["language"],
                code=s["code"],
                status=s["status"],
                details=s.get("details", []),
                score=s.get("score", 0),
                counts=s.get("counts", 1),
            )
            db.merge(submission)
        db.commit()
        return make_response(200, "import success", None)
    except:
        db.rollback()
        return make_response(400, "invalid JSON format", None)
