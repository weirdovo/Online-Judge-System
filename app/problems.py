from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas import Problem_
from app.models import Problem
from app.utils import make_response, admin_guard, get_db

router = APIRouter()

@router.get("/api/problems/")
async def list_problems(request : Request, db : Session = Depends(get_db)):
    # if "user_id" not in request.session:
    #     return make_response(401, "not logged in", None)
    return make_response(200, "success", 
                         [{"id" : x.id, "title" : x.title} for x in db.query(Problem).all()])
    
@router.post("/api/problems/")
async def add_problem(problem : Problem_, request : Request, db : Session = Depends(get_db)):
    if "user_id" not in request.session:
        return make_response(401, "not logged in", None)
    new_problem = Problem(**problem.model_dump())
    db.add(new_problem)
    try:
        db.commit()
        db.refresh(new_problem)
        return make_response(200, "add success", {"id" : f"{problem.id}"})
    except IntegrityError:
        db.rollback() 
        return make_response(409, "id already existed", None)

@router.delete("/api/problems/{id}")
async def delete_problem(id : str, request : Request, db : Session = Depends(get_db)):
    if not admin_guard(request):
        return make_response(401, "permission denied", None)
    problem = db.query(Problem).filter_by(id = id).first()
    if not problem:
        return make_response(404, "problem does not exist", None)
    db.delete(problem)
    db.commit()
    return make_response(200, "delete success", {"id" : id})


@router.get("/api/problems/{id}")
async def get_problem(id : str, db : Session = Depends(get_db)):
    
    problem = db.query(Problem).filter_by(id = id).first()
    if not problem:
        return make_response(404, "problem does not exist", None)
    return make_response(200, "success", problem.to_dict())

    
