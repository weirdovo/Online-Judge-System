from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.db import Localsession
from app.models import User, Problem, Submission, Language, LogHistory
from app.utils import get_db, make_response, admin_guard
from app.judge import run_judge
from app.schemas import submission, submission_list
import asyncio

router = APIRouter(prefix = "/api/submissions")

@router.post("/")
async def submit_code(request : Request, submiss : submission, db : Session = Depends(get_db)):
    language = db.query(Language).filter_by(name = submiss.language).first()
    if not language:
        return make_response(400, "invalid params", None)
    user_id = request.session.get("user_id")
    if not user_id:
        return make_response(401, "not logged in", None)
    user = db.query(User).filter_by(id = user_id).first()
    if user.is_banned:
        return make_response(403, "permission denied", None)
    problem = db.query(Problem).filter_by(id = submiss.problem_id).first()
    if not problem:
        return make_response(404, "problem does not exist", None)
    
    # control the frequency of requests
    
    sub = Submission(problem = problem, user = user,
                     code = submiss.code, status = "pending", language = submiss.language)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    new_db = Localsession()  # new session!!!
    asyncio.create_task(run_judge(sub.id, submiss, new_db))
    return make_response(200, "success", {"submission_id" : sub.id, "status" : "pending"})
    
    
@router.get("/{submission_id}")
async def get_result(request : Request, submission_id : int, db : Session = Depends(get_db)):
    this_id = request.session.get("user_id")
    if not this_id:
        return make_response(401, "not logged in", None)
    task = db.query(Submission).filter_by(id = submission_id).first()
    if not task:
        return make_response(404, "submission does not exist", None)
    if admin_guard(request) and this_id != task.user_id:
        return make_response(403, "permission denied", None)
    if not task:
        return make_response(404, "submission does not exist", None)
    return make_response(200, "success", {"score" : task.score, "counts" : task.counts})

@router.get("/")
async def get_submission(request : Request, lis : submission_list = Depends(), db : Session = Depends(get_db)):
    if not lis.valid_params():
        return make_response(400, "invalid params", None)
    user_id = request.session.get("user_id")
    if not user_id:
        return make_response(401, "not logged in", None)
    if admin_guard(request) and (lis.user_id is not None and user_id != lis.user_id):
        return make_response(403, "permission denied", None)
    if admin_guard(request) and (lis.user_id is None):
        lis.user_id = user_id
    
    query = db.query(Submission)
    if lis.user_id is not None:
        query = query.filter(Submission.user_id == lis.user_id)
    if lis.problem_id is not None:
        query = query.filter(Submission.problem_id == lis.problem_id)
    if lis.status is not None:
        query = query.filter(Submission.status == lis.status)    
    total = query.count()
    if lis.page_size is not None:
        offset = (lis.page - 1) * lis.page_size
        query = query.offset(offset).limit(lis.page_size)
    
    submissions = query.all()
    result = []
    for sub in submissions:
        if sub.status in ("error", "pending"):
            result.append({
                "submission_id": sub.id,
                "status": sub.status
            })
        else:
            result.append({
                "submission_id": sub.id,
                "status": sub.status,
                "score": sub.score,
                "counts": sub.counts
            })
    return make_response(200, "success", {"total" : total, "submissions" : result})
                                            
@router.put("/{submission_id}/rejudge")
async def rejudge(request : Request, submission_id : int, db : Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return make_response(401, "not logged in", None)
    if admin_guard(request):
        return make_response(403, "permission denied", None)
    sub = db.query(Submission).filter_by(id = submission_id).first()
    if sub is None:
        return make_response(404, "submission does not exist", None)
    sub.rejudge_init()
    db.commit()
    db.refresh(sub)
    asyncio.create_task(run_judge(sub.id, sub.code, sub.problem))
    return make_response(200, "rejudge started", {"submission_id" : sub.id, "status" : "pending"})

@router.get("/{submission_id}/log")
async def get_log(request : Request, submission_id : int, db : Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return make_response(401, "not logged in", None)
    sub = db.query(Submission).filter_by(id = submission_id).first()
    if not sub:
        return make_response(404, "submission does not exist", None)
    
    log_his = LogHistory(user_id = user_id, problem_id = sub.problem_id)
    if admin_guard(request) and sub.user_id != user_id and sub.problem.public_cases is False:
        log_his.status = 403
        db.add(log_his)
        db.commit()
        db.refresh(log_his)
        return make_response(403, "permission denied", None)
    data = {
        "details" : sub.detail,
        "score" : sub.score,
        "counts" : sub.counts
    }
    log_his.status = 200
    db.add(log_his)
    db.commit()
    db.refresh(log_his)
    return make_response(200, "success", data)
