import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self, config):
        self.config = config
        self.tasks = []

    def add_task(self, task, run_at):
        self.tasks.append({
            'task': task,
            'run_at': run_at
        })
        logger.info(f"Task scheduled for {run_at}")

    async def run(self):
        while True:
            now = datetime.now()
            for task in self.tasks:
                if now >= task['run_at']:
                    logger.info(f"Running scheduled task at {now}")
                    await task['task']()
                    self.tasks.remove(task)
            await asyncio.sleep(60)  # Check every minute

    def schedule_assignment(self, assignment_data):
        due_date = datetime.strptime(assignment_data['due_date'], "%Y-%m-%d %H:%M:%S")
        run_at = due_date - timedelta(days=1)  # Run 1 day before due date
        self.add_task(lambda: self.process_assignment(assignment_data), run_at)

    async def process_assignment(self, assignment_data):
        # This method should contain the logic to process an assignment
        # You'll need to adapt this to work with your existing code
        pass
