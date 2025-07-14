import subprocess
import tempfile
import threading
import psutil
import time
import os
import asyncio

from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Problem, Submission
from app.utils import get_db

async def run_judge(id : int, code : str, db : Session = Depends(get_db)):
    task = db.query(Submission).filter_by(id = id).first()
    problem = db.query(Problem).filter_by(id = task.problem_id).first()
    try:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as tmp_code:
            tmp_code.write(code)
            tmp_code.flush()
            code_path = tmp_code.name
        score = 0
        detail = []
        counts = len(problem.testcases) * 10
        for i, case in enumerate(problem.testcases):
            status = await asyncio.to_thread(judge_case, case, task.language, 
                                             problem.time_limit, problem.memory_limit, code_path)
            status["id"] = i+1
            if status["status"] == "AC":
                score = score + 10
            detail.append(status)
        task.status = "success"
        task.counts = counts
        task.score = score
        task.detail = detail    
        db.commit()
        db.refresh(task)
    except Exception as e:
        task.status = "error"
        db.commit()
        db.refresh(task)
    finally:
        if 'code_path' in locals() and os.path.exists(code_path):
            os.remove(code_path)

def judge_case(case, language : str, tl : float, ml : int, code_path : str):
    result_holder = {"status" : "OK", "time" : 0.0, "memory" : 0}
    with tempfile.NamedTemporaryFile(mode = 'w+', delete = False) as tmp_in:
        tmp_in.write(case["input"])
        tmp_in.flush()
        try:
            proc = subprocess.Popen(
                [language, code_path],
                stdin=open(tmp_in.name, "r"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            memory_monitor = threading.Thread(
                target = monitor_memory,
                args = (proc, ml, result_holder)
            )
            memory_monitor.start()
            start = time.time()
            try:
                stdout, stderr = proc.communicate(timeout = tl)
                end = time.time()
                result_holder["time"] =round(end - start, 3)
                output = stdout.decode().strip()
                if result_holder["status"] != "OK":
                    return result_holder
                if "SyntaxError" in stderr.decode():
                    result_holder["status"] = "CE"
                if proc.returncode != 0:
                    result_holder["status"] = "RE"
                
                if output == case["output"].strip():
                    result_holder["status"] = "AC"
                else:
                    result_holder["status"] = "WA"
            except subprocess.TimeoutExpired:
                proc.kill()
                result_holder["status"] = "TLE"
                result_holder["time"] = tl
            finally:
                memory_monitor.join()
        except Exception:
            result_holder["status"] = "UNK"
        finally:
            os.remove(tmp_in.name)
    return result_holder

def monitor_memory(proc, mem_limit_mb, result_holder):
    try:
        p = psutil.Process(proc.pid)
        peak = 0
        while proc.poll() is None:
            mem_usage = p.memory_info().rss / (1024 ** 2)  # in MB
            peak = max(peak, mem_usage)
            if mem_usage > mem_limit_mb:
                proc.kill()
                result_holder["status"] = "MLE"
                return
            time.sleep(0.05)
        result_holder["memory"] = round(peak, 2)
    except Exception:
        result_holder["status"] = "UNK"
        result_holder["memory"] = -1