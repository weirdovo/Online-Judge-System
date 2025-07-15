from pydantic import BaseModel
from typing import Optional, List

class New_User(BaseModel):
    username : str
    password : str

class Role(BaseModel):
    role : str

class Cases(BaseModel):
    input : str
    output : str

# the correct format of problem
class Problem_(BaseModel):
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
    
class submission(BaseModel):
    problem_id : str
    language : str
    code : str
    
class submission_list(BaseModel):
    user_id : Optional[int] = None
    problem_id : Optional[str] = None
    status : Optional[str] = "success"
    page : Optional[int] = None
    page_size : Optional[int] = None
    
    def valid_params(self):
        if self.user_id is None and self.problem_id is None:
            return False
        if self.page is None:
            self.page = 1
        elif self.page is not None and self.page_size is None:
            return False
        if self.status not in ["success", "pending", "error"]:
            return False
        return True
    
class new_language(BaseModel):
    name : str
    file_ext : str
    compile_cmd : Optional[str] = None
    run_cmd : str
    time_limit : Optional[float] = None
    memory_limit : Optional[int] = None
    
class public_cases(BaseModel):
    public_cases : bool = False