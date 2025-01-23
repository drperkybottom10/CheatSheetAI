import asyncio
from typing import List, Dict
import json

class ProgressTracker:
    def __init__(self):
        self.tasks: List[Dict[str, any]] = []
        self.current_task_index: int = 0

    async def add_task(self, task_name: str, total_steps: int):
        self.tasks.append({
            "name": task_name,
            "total_steps": total_steps,
            "completed_steps": 0,
            "status": "pending"
        })

    async def update_task_progress(self, task_index: int, completed_steps: int):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["completed_steps"] = completed_steps
            if completed_steps >= self.tasks[task_index]["total_steps"]:
                self.tasks[task_index]["status"] = "completed"
            else:
                self.tasks[task_index]["status"] = "in_progress"

    async def get_overall_progress(self) -> float:
        total_steps = sum(task["total_steps"] for task in self.tasks)
        completed_steps = sum(task["completed_steps"] for task in self.tasks)
        return completed_steps / total_steps if total_steps > 0 else 0

    async def save_progress(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.tasks, f)

    async def load_progress(self, filename: str):
        try:
            with open(filename, 'r') as f:
                self.tasks = json.load(f)
        except FileNotFoundError:
            pass

    async def get_next_pending_task(self) -> Dict[str, any]:
        for task in self.tasks:
            if task["status"] == "pending":
                return task
        return None
