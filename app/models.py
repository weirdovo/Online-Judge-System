from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, Float
from app.db import Base
from app.utils import get_time

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique = True, index = True)
    password = Column(String)
    role = Column(String, default = "user")
    join_time = Column(String, default = get_time())
    submit_count = Column(String , default = 0)
    resolve_count = Column(String , default = 0)
    is_banned = Column(Boolean, default = False)
        
class Problem(Base):
    __tablename__ = "problems"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    input_description = Column(Text, nullable=False)
    output_description = Column(Text, nullable=False)
    samples = Column(JSON, nullable=False)     
    constraints = Column(Text, nullable=False)
    testcases = Column(JSON, nullable=False)
    
    hint = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    time_limit = Column(Float, nullable=True)
    memory_limit = Column(Integer, nullable=True)
    author = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    
    def to_dict(self):
        return {"id" : self.id,
                "title" : self.title,
                "description" : self.description,
                "input_description" : self.input_description,
                "output_description" : self.output_description,
                "samples" : self.samples,
                "constraints" : self.constraints,
                "testcases" : self.testcases,
                "hint" : self.hint if self.hint is not None else "",
                "source" : self.source if self.source is not None else "",
                "tags" : self.tags if self.tags is not None else [],
                "time_limit" : self.time_limit if self.time_limit is not None else 0.0,
                "memory_limit" : self.memory_limit if self.memory_limit is not None else 0,
                "author" : self.author if self.author is not None else "",
                "difficulty" : self.difficulty if self.difficulty is not None else ""
                }