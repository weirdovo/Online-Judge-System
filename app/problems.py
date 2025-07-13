from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List

from app.utils import make_response, admin_guard

router = APIRouter()
problem_set = {}  # problem_id : problem (class Problem)

class Cases(BaseModel):
    input : str
    output : str

# Correct format of problem
class Problem(BaseModel):
    id: str
    title: str
    description: str
    input_description: str
    output_description: str
    samples: List[Cases]
    constraints: str
    testcases: List[Cases]
    hint: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    time_limit: Optional[float] = None
    memory_limit: Optional[int] = None
    author: Optional[str] = None
    difficulty: Optional[str] = None
    

@router.get("/api/problems/")
async def list_problems(request : Request):
    if "user_id" not in request.session:
        return make_response(401, "not logged in", None)
    return make_response(200, "success", [{"id" : x.id, "title" : x.title} for x in problem_set.values()])
    
@router.post("/api/problems/")
async def add_problem(problem: Problem, request: Request):
    if "user_id" not in request.session:
        return make_response(401, "not logged in", None)
    
    if problem.id in problem_set:
        return make_response(409, "id already existed", None)
    else:
        problem_set[problem.id] = problem
        return make_response(200, "add success", {"id" : f"{problem.id}"})

@router.delete("/api/problems/{id}")
async def delete_problem(id: str, request: Request):
    if not admin_guard(request):
        return make_response(401, "permission denied", None)
    if id in problem_set:
        del problem_set[id]
        return make_response(200, "delete success", {"id" : id})
    else:
        return make_response(404, "problem does not exist", None)

@router.get("/api/problems/{id}")
async def get_problem(id):
    if id in problem_set:
        return make_response(200, "success", problem_set[id].dict())
    else:
        return make_response(404, "problem does not exist", None)
    
