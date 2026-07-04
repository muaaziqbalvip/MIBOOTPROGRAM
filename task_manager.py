"""
MI AI - Task Manager
Chote-mote tasks track karne ke liye (per-user, in-memory).
"""

import json
import os

TASKS_FILE = "/tmp/mi_ai_files/tasks.json"


def _load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_tasks(tasks):
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def add_task(user_id: str, task_text: str):
    tasks = _load_tasks()
    tasks.setdefault(str(user_id), [])
    tasks[str(user_id)].append({"text": task_text, "done": False})
    _save_tasks(tasks)


def list_tasks(user_id: str) -> list:
    tasks = _load_tasks()
    return tasks.get(str(user_id), [])


def complete_task(user_id: str, index: int) -> bool:
    tasks = _load_tasks()
    user_tasks = tasks.get(str(user_id), [])
    if 0 <= index < len(user_tasks):
        user_tasks[index]["done"] = True
        _save_tasks(tasks)
        return True
    return False


def clear_tasks(user_id: str):
    tasks = _load_tasks()
    tasks[str(user_id)] = []
    _save_tasks(tasks)


def format_task_list(user_id: str) -> str:
    tasks = list_tasks(user_id)
    if not tasks:
        return "📋 Koi task nahi hai. `/addtask <kaam>` se add karein."

    lines = ["📋 **Aapke Tasks:**\n"]
    for i, t in enumerate(tasks):
        status = "✅" if t["done"] else "⬜"
        lines.append(f"{status} {i + 1}. {t['text']}")
    return "\n".join(lines)