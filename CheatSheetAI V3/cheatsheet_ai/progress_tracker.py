import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProgressTracker:
    def __init__(self):
        self.steps = []
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = datetime.now()
        logger.info("Assignment processing started.")

    def add_step(self, step_name):
        self.steps.append({
            'name': step_name,
            'time': datetime.now()
        })
        logger.info(f"Completed step: {step_name}")

    def end(self):
        self.end_time = datetime.now()
        logger.info("Assignment processing completed.")

    def generate_report(self):
        if not self.start_time or not self.end_time:
            return "Progress tracking not properly initialized or completed."

        total_time = (self.end_time - self.start_time).total_seconds()
        report = f"Assignment Processing Report\n"
        report += f"Total time: {total_time:.2f} seconds\n\n"
        report += "Steps:\n"
        
        for i, step in enumerate(self.steps, 1):
            step_time = (step['time'] - self.start_time).total_seconds()
            report += f"{i}. {step['name']} - {step_time:.2f} seconds\n"

        return report
