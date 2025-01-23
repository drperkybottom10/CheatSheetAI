import asyncio
import logging
from config import load_config
from browser_use import Agent, Browser
from canvas_manager import CanvasManager
from google_docs_manager import GoogleDocsManager
from assignment_handler import AssignmentHandler
from ui_manager import UIManager
from langchain_google_vertexai import ChatVertexAI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    config = load_config()
    browser = Browser(config=config.browser_config)
    llm = ChatVertexAI(model="gemini-1.5-flash")
    canvas_manager = CanvasManager(browser)
    google_docs_manager = GoogleDocsManager(browser)
    assignment_handler = AssignmentHandler(canvas_manager, google_docs_manager)
    ui_manager = UIManager()

    try:
        await ui_manager.start()
        agent = Agent(task="Log into Canvas and get all assignments", llm=llm, browser=browser)
        history = await agent.run()
        assignments = history.extracted_content()
        for assignment in assignments:
            await assignment_handler.handle_assignment(assignment)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
