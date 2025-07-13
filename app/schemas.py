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