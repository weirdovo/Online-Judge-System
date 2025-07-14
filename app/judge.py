import subprocess
import tempfile
import threading
import psutil
import time
import os

def judge(case, language : str, tl : float, ml : int):
    result_holder = {"status" : "OK", "time" : 0.0, "memory" : 0}
    with tempfile.NamedTemporaryFile(mode = 'w+', delete = False) as tmp_in:
        tmp_in.write(case["input"])
        tmp_in.flush()
        try:
            proc = subprocess.Popen(
                [language, "test_submission.py"],
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
                result_holder["time"] =round(start - end)
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