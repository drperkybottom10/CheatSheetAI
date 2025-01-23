import asyncio
import logging
from dotenv import load_dotenv
import sys
from cheatsheet_ai.config import Config
from cheatsheet_ai.browser_manager import BrowserManager
from cheatsheet_ai.canvas_handler import CanvasHandler
from cheatsheet_ai.google_handler import GoogleHandler
from cheatsheet_ai.assignment_processor import AssignmentProcessor
from cheatsheet_ai.llm_manager import LLMManager
from cheatsheet_ai.error_handler import CheatSheetAIException
from cheatsheet_ai.progress_tracker import ProgressTracker
from cheatsheet_ai.scheduler import Scheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("cheatsheet_ai.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

async def main():
    try:
        # Load environment variables
        load_dotenv()

        # Initialize configuration
        config = Config()

        # Initialize components
        browser_manager = BrowserManager(config)
        llm_manager = LLMManager(config)
        canvas_handler = CanvasHandler(browser_manager, config)
        google_handler = GoogleHandler(browser_manager, config)
        assignment_processor = AssignmentProcessor(llm_manager, config)
        progress_tracker = ProgressTracker()
        scheduler = Scheduler(config)

        progress_tracker.start()
        # Login to Canvas
        await canvas_handler.login()
        progress_tracker.add_step("Logged into Canvas")

        # Get all assignments
        assignments = await canvas_handler.get_all_assignments()
        progress_tracker.add_step("Retrieved all assignments")

        # Schedule assignments
        for assignment in assignments:
            scheduler.schedule_assignment(assignment)
        progress_tracker.add_step("Scheduled all assignments")

        # Run the scheduler
        await scheduler.run()

    except CheatSheetAIException as e:
        logger.error(f"CheatSheet AI error: {str(e)}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {str(e)}")
    finally:
        await browser_manager.close()
        progress_tracker.end()
        logger.info(progress_tracker.generate_report())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("CheatSheet AI terminated by user.")
        sys.exit(0)
