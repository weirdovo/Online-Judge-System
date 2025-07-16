import subprocess
import tempfile
import threading
import psutil
import time
import os
import asyncio
import shlex

from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Problem, Submission, Language
from app.schemas import submission
from app.utils import get_db


async def run_judge(id: int, sub: submission, db: Session = Depends(get_db)):
    task = db.query(Submission).filter_by(id=id).first()
    problem = db.query(Problem).filter_by(id=task.problem_id).first()
    language = db.query(Language).filter_by(name=sub.language).first()
    code = sub.code
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = os.path.join(tmpdir, "code" + language.file_ext)
            exe_path = os.path.join(tmpdir, "exec.out")
            with open(src_path, "w") as f:
                f.write(code)
            if language.compile_cmd:
                compile_cmd = language.compile_cmd.format(src=src_path, exe=exe_path)
                compile_proc = subprocess.run(
                    shlex.split(compile_cmd), capture_output=True
                )
                if compile_proc.returncode != 0:
                    task.status = "error"
                    task.detail = {"status": "CE"}
                    db.commit()
                    return
            else:
                exe_path = src_path
            score = 0
            detail = []
            counts = len(problem.testcases) * 10
            for i, case in enumerate(problem.testcases):
                run_cmd = language.run_cmd.format(src=src_path, exe=exe_path)
                status = await asyncio.to_thread(
                    judge_case, case, run_cmd, problem.time_limit, problem.memory_limit
                )
                status["id"] = i + 1
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
        # ???
        db.commit()
        db.refresh(task)


def judge_case(case, run_cmd: str, tl: float, ml: int):
    result_holder = {"status": "OK", "time": 0.0, "memory": 0}
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_in:
        tmp_in.write(case["input"])
        tmp_in.flush()
        try:
            proc = subprocess.Popen(
                shlex.split(run_cmd),
                stdin=open(tmp_in.name, "r"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            memory_monitor = threading.Thread(
                target=monitor_memory, args=(proc, ml, result_holder)
            )
            memory_monitor.start()
            start = time.time()
            try:
                stdout, stderr = proc.communicate(timeout=tl)
                end = time.time()
                result_holder["time"] = round(end - start, 3)
                output = stdout.decode().strip()
                if result_holder["status"] != "OK":
                    return result_holder
                if proc.returncode != 0:
                    if "SyntaxError" in stderr.decode() or "error:" in stderr.decode():
                        result_holder["status"] = "CE"
                    else:
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
            mem_usage = p.memory_info().rss / (1024**2)  # in MB
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
