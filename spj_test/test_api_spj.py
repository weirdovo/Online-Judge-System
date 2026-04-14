import uuid
import os
import pytest
from test_helpers import setup_admin_session

def test_create_union_problem_with_spj(client):
    setup_admin_session(client)

    # Create problem
    problem_id = "union_" + uuid.uuid4().hex[:6]
    problem_data = {
        "id": problem_id,
        "title": "集合并集判断",
        "description": "给定两个整数集合，输出它们的并集。",
        "input_description": "输入两行，分别为集合 A 和 B，空格分隔。",
        "output_description": "输出一行并集。",
        "samples": [
            {
                "input": "1 2 3\n2 4 5",
                "output": "1 2 3 4 5"
            }
        ],
        "constraints": "每个集合最多不超过 100 个元素，范围为 0 到 1000。",
        "testcases": [
            {
                "input": "1 2 3\n2 4 5",
                "output": "1 2 3 4 5"
            },
            {
                "input": "10 20\n30 40",
                "output": "10 20 30 40"
            },
            {
                "input": "5 206 0\n1 4 0 ",
                "output": "206 0 1 4 5"
            }
        ],
        "time_limit": 1.0,
        "memory_limit": 128,
        "public_cases": True
    }

    resp = client.post("/api/problems/", json=problem_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["msg"] == "add success"

    # Upload SPJ script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    spj_path = os.path.join(BASE_DIR, "../app/spj_scripts/spj.py")
    assert os.path.exists(spj_path)

    with open(spj_path, "rb") as f:
        resp = client.post(
            f"/api/problems/{problem_id}/spj",
            files={"file": ("spj.py", f, "application/octet-stream")}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["msg"] == "judge mode updated"


def test_delete_union_problem_spj(client):
    setup_admin_session(client)
    problem_id = "union_" + uuid.uuid4().hex[:6]
    problem_data = {
        "id": problem_id,
        "title": "集合并集判断",
        "description": "给定两个整数集合，输出它们的并集。",
        "input_description": "输入两行，分别为集合 A 和 B，空格分隔。",
        "output_description": "输出一行并集。",
        "samples": [
            {
                "input": "1 2 3\n2 4 5",
                "output": "1 2 3 4 5"
            }
        ],
        "constraints": "每个集合最多不超过 100 个元素，范围为 0 到 1000。",
        "testcases": [
            {
                "input": "1 2 3\n2 4 5",
                "output": "1 2 3 4 5"
            },
            {
                "input": "10 20\n30 40",
                "output": "10 20 30 40"
            },
            {
                "input": "5 206 0\n1 4 0 ",
                "output": "206 0 1 4 5"
            }
        ],
        "time_limit": 1.0,
        "memory_limit": 128,
        "public_cases": True
    }

    resp = client.post("/api/problems/", json=problem_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["msg"] == "add success"


    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    spj_path = os.path.join(BASE_DIR, "../app/spj_scripts/spj.py")
    with open(spj_path, "rb") as f:
        resp = client.post(
            f"/api/problems/{problem_id}/spj",
            files={"file": ("spj.py", f, "application/octet-stream")}
        )
    assert resp.status_code == 200

    resp = client.delete(f"/api/problems/{problem_id}/spj")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert data["msg"] == "spj script deleted"

    resp = client.delete(f"/api/problems/{problem_id}/spj")
    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == 400
    assert data["msg"] == "no spj script to delete"

    resp = client.get(f"/api/problems/{problem_id}")
    assert resp.status_code == 200
    problem_info = resp.json()
    assert problem_info["data"]["judge_mode"] == "standard"