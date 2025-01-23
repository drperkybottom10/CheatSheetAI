import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

class AssignmentPrioritizer:
    def __init__(self):
        self.assignments: List[Dict[str, any]] = []

    async def add_assignment(self, assignment: Dict[str, any]):
        self.assignments.append(assignment)

    async def prioritize_assignments(self) -> List[Dict[str, any]]:
        def priority_score(assignment: Dict[str, any]) -> float:
            due_date = datetime.fromisoformat(assignment['due_date'])
            time_until_due = (due_date - datetime.now()).total_seconds()
            weight = assignment.get('weight', 1)
            estimated_time = assignment.get('estimated_time', 60)  # in minutes

            # Higher score means higher priority
            return (weight * 1000000) / (time_until_due * estimated_time)

        return sorted(self.assignments, key=priority_score, reverse=True)

    async def get_next_assignment(self) -> Dict[str, any]:
        prioritized = await self.prioritize_assignments()
        return prioritized[0] if prioritized else None

    async def update_assignment_status(self, assignment_id: str, status: str):
        for assignment in self.assignments:
            if assignment['id'] == assignment_id:
                assignment['status'] = status
                break

    async def get_assignments_due_soon(self, days: int = 3) -> List[Dict[str, any]]:
        now = datetime.now()
        soon = now + timedelta(days=days)
        return [
            assignment for assignment in self.assignments
            if now <= datetime.fromisoformat(assignment['due_date']) <= soon
        ]
