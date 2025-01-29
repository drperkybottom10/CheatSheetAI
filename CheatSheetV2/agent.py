from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, BrowserConfig, Browser
from browser_use.browser.context import BrowserContextConfig
from browser_use.controller.service import Controller, ActionResult
import asyncio
from dotenv import load_dotenv
import json
import os
from typing import Optional, List, Callable
import logging
from CheatSheetV2.assignment_types import handle_quiz
from ml_component import MLComponent, extract_features, create_label
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
import tiktoken
from pydantic import BaseModel

# Import new modules
from login import login_to_canvas
from course_navigation import search_for_course, navigate_to_course
from assignment_navigation import search_for_assignment, navigate_to_assignment
from assignment_details import extract_assignment_details
from assignment_completion import fill_in_assignment, complete_assignment, submit_assignment
from google_docs import create_blank_doc, make_copy_of_google_doc, filter_google_docs_links, handle_google_doc
from utils import generate_assignment_response, check_plagiarism, set_reminders, analyze_assignment_description

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-002')

# Initialize browser configuration with headless mode for speed
browser_config = BrowserConfig(
    headless=False,  # Enable headless mode for faster execution
    disable_security=True,  # Ensure this is compatible with the latest browser-use library
    extra_chromium_args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--start-maximized',
        '--no-first-run',
        '--no-default-browser-check',
        '--no-sandbox',   # FASTER: often needed for performance in certain environments
        '--disable-gpu',  # FASTER: remove GPU overhead
        '--disable-extensions',
        '--enable-features=NetworkService,NetworkServiceInProcess'
    ]
)

# Initialize context configuration with optimized settings
context_config = BrowserContextConfig(
    wait_for_network_idle_page_load_time=0.1,   # FASTER: drastically reduced
    browser_window_size={'width': 1280, 'height': 1100},
    minimum_wait_page_load_time=0.1,           # FASTER
    maximum_wait_page_load_time=2.0            # FASTER
)

# Update browser config with context config
browser_config.new_context_config = context_config

# Initialize the LLM with the correct model name (now using gemini-2.0-flash-exp)
llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash-002',
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Initialize ML component
ml_component = MLComponent()

# Pydantic models for structured parameters
class GoogleCredentials(BaseModel):
    email: str
    password: str

class DocumentDetails(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None
    title: Optional[str] = None
    is_assignment: bool = False

class AssignmentData(BaseModel):
    description: str
    instructions: str
    links: List[str] = []
    attachments: List[str] = []

class FillAssignmentDetails(BaseModel):
    doc_url: str
    assignment_content: str

class AssignmentSubmissionDetails(BaseModel):
    assignment_url: str
    submission_type: str
    file_path: Optional[str] = None
    text_content: Optional[str] = None

class SearchCourseParams(BaseModel):
    course_name: str

class NavigateCourseParams(BaseModel):
    course_selector: str

class SearchAssignmentParams(BaseModel):
    assignment_name: str

class NavigateAssignmentParams(BaseModel):
    assignment_selector: str

class CompleteAssignmentParams(BaseModel):
    assignment_details: dict

# Define new Pydantic model for DocumentCopyDetails
class DocumentCopyDetails(BaseModel):
    original_url: str
    new_title: Optional[str] = None  # Ensure optional title handling is consistent

# Initialize controller
controller = Controller()

# Register custom actions with optimized implementations
controller.action("Login to Canvas", param_model=GoogleCredentials)(login_to_canvas)
controller.action("Search for course", param_model=SearchCourseParams)(search_for_course)
controller.action("Navigate to Course", param_model=NavigateCourseParams)(navigate_to_course)
controller.action("Search for assignment", param_model=SearchAssignmentParams)(search_for_assignment)
controller.action("Navigate to Assignment", param_model=NavigateAssignmentParams)(navigate_to_assignment)
controller.action("Extract assignment details")(extract_assignment_details)
controller.action("Fill in assignment", param_model=FillAssignmentDetails)(fill_in_assignment)
controller.action("Complete assignment", param_model=CompleteAssignmentParams)(complete_assignment)
controller.action("Submit assignment", param_model=AssignmentSubmissionDetails)(submit_assignment)
controller.action("Generate assignment response")(generate_assignment_response)
controller.action("Check plagiarism")(check_plagiarism)
controller.action("Set reminders")(set_reminders)
controller.action("handle_google_doc", param_model=DocumentDetails)(handle_google_doc)

async def run_agent_task(agent_task: str, llm: ChatGoogleGenerativeAI, controller: Controller, browser: Browser):
    agent = Agent(
        task=agent_task,
        llm=llm,
        controller=controller,
        use_vision=True,
        save_conversation_path="logs/conversation.json",
        browser=browser  # Ensure browser object is correctly initialized
    )
    try:
        result = await agent.run()
        if not result:
            raise ValueError("Agent returned an empty result")
        
        # Attempt to parse the result
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse agent result: {result}")
            raise ValueError("Could not parse agent result as JSON")
        
        logger.info(f"Agent task completed successfully: {parsed_result}")
        return result
    except Exception as e:
        logger.error(f"Agent run failed: {str(e)}", exc_info=True)
        # Train ML model with the result
        features = extract_features(str(result))
        label = create_label(str(result))
        ml_component.train(features, [label])
        return f"Agent run failed: {str(e)}"

executor = ThreadPoolExecutor(max_workers=5)

async def run_action(action_name: str, **kwargs) -> ActionResult:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: controller.run_action(action_name, **kwargs)
    )
    # Use ML model to predict success of action
    features = extract_features(str(result))
    prediction = ml_component.predict(features)
    logger.info(f"ML prediction for action {action_name}: {prediction}")
    return result

async def run_actions_concurrently(*actions):
    tasks = []
    for action in actions:
        tasks.append(run_action(**action))
    results = await asyncio.gather(*tasks)
    return results

async def main(progress_callback: Optional[Callable[[str], None]] = None):
    try:
        # Validate environment variables
        logger.info("Validating environment variables...")
        required_env_vars = [
            "USERNAME", "PASSWORD", "COURSE_SELECTOR",
            "ASSIGNMENT_SELECTOR", "GOOGLE_EMAIL",  # Ensure all required variables are validated
            "GOOGLE_PASSWORD", "PROVIDED_GOOGLE_DOC_URL",
            "GOOGLE_API_KEY"
        ]

        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if (missing_vars):
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

        if progress_callback:
            progress_callback("Environment variables validated successfully.")
        logger.info("Environment variables validated successfully.")

        # Get environment variables
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        course_selector = os.getenv("COURSE_SELECTOR")
        assignment_selector = os.getenv("ASSIGNMENT_SELECTOR")
        google_email = os.getenv("GOOGLE_EMAIL")
        google_password = os.getenv("GOOGLE_PASSWORD")
        provided_google_doc_url = os.getenv("PROVIDED_GOOGLE_DOC_URL")

        # Define the main task with a shorter, more concise format
        main_task = f"""
        1. Go to baps.instructure.com/login, close any errors
        2. Login with user='{username}', pass='{password}'
        3. Click course '{course_selector}'
        4. Click assignment '{assignment_selector}'
        5. Read assignment details and get links
        6. For Google Doc links:
           - Login: '{google_email}'/'{google_password}'
           - Make copy and complete assignment
        7. If quiz, enter access code if needed
        8. Never click submission attempts or downloads
        9. Generate assignment response
        10. Check for plagiarism
        11. Set reminders for due dates
        12. Submit the completed assignment
        """

        # Initialize the browser without calling a nonexistent 'start' method
        browser = Browser(config=browser_config)

        try:
            # Run the main agent task
            main_result = await run_agent_task(main_task, llm, controller, browser)
            logger.info(f"Main agent task result: {main_result}")
            
            # Check if the task was actually completed
            if "completed successfully" not in str(main_result).lower():
                raise Exception("Task was not completed successfully")

            # Extract Google Docs links from the assignment details
            assignment_details = await extract_assignment_details(browser)
            doc_links = await filter_google_docs_links(assignment_details["links"])
            
            # Verify that we're on the correct assignment page
            if assignment_selector.lower() not in assignment_details["title"].lower():
                logger.warning(f"Navigated to incorrect assignment: {assignment_details['title']}")
                # Implement course correction here
                await navigate_to_correct_assignment(browser, assignment_selector)
                assignment_details = await extract_assignment_details(browser)
            
            # Process the assignment based on its type
            if assignment_details["type"] == "quiz":
                await handle_quiz(assignment_details, browser)
            elif doc_links:
                await process_google_docs(doc_links, assignment_details, browser)
            else:
                await handle_other_assignment_type(assignment_details, browser)
            
        except Exception as e:
            logger.error(f"An error occurred while processing the main task: {str(e)}")
            if progress_callback:
                progress_callback(f"An error occurred: {str(e)}")
            
            # Implement error recovery and course correction
            await error_recovery_and_course_correction(browser, e)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return "CheatSheet AI process completed."

async def navigate_to_correct_assignment(browser: Browser, assignment_selector: str):
    try:
        logger.info(f"Attempting to navigate to the correct assignment: {assignment_selector}")
        await browser.goto("https://baps.instructure.com/")
        await asyncio.sleep(2)
        
        # Navigate to the correct course
        course_selector = os.getenv("COURSE_SELECTOR")
        course_link = await browser.query_selector(f"a:has-text('{course_selector}')")
        if course_link:
            await course_link.click()
            await browser.wait_for_navigation()
        
        # Find and click on the correct assignment
        assignment_link = await browser.query_selector(f"a:has-text('{assignment_selector}')")
        if assignment_link:
            await assignment_link.click()
            await browser.wait_for_navigation()
        else:
            raise Exception(f"Could not find assignment: {assignment_selector}")
        
        logger.info(f"Successfully navigated to assignment: {assignment_selector}")
    except Exception as e:
        logger.error(f"Failed to navigate to correct assignment: {str(e)}")
        raise

async def process_google_docs(doc_links: List[str], assignment_details: dict, browser: Browser):
    try:
        for doc_link in doc_links:
            doc_details = DocumentDetails(url=doc_link, is_assignment=True)
            await handle_google_doc(doc_details, browser)
    except Exception as e:
        logger.error(f"Error processing Google Docs: {str(e)}")
        raise

async def error_recovery_and_course_correction(browser: Browser, error: Exception):
    try:
        logger.info(f"Attempting error recovery and course correction for error: {str(error)}")
        # Check if we're logged out
        if "login" in browser.url.lower():
            await login_to_canvas(GoogleCredentials(email=os.getenv("USERNAME"), password=os.getenv("PASSWORD")), browser)
        
        # If we're on an unexpected page, try to navigate back to the main course page
        course_selector = os.getenv("COURSE_SELECTOR")
        assignment_selector = os.getenv("ASSIGNMENT_SELECTOR")
        if course_selector not in await browser.title():
            await browser.goto("https://baps.instructure.com/")
            await asyncio.sleep(2)
            course_link = await browser.query_selector(f"a:has-text('{course_selector}')")
            if course_link:
                await course_link.click()
                await browser.wait_for_navigation()
        
        # Try to find and navigate to the correct assignment again
        await navigate_to_correct_assignment(browser, assignment_selector)
        logger.info("Error recovery and course correction completed")
    except Exception as e:
        logger.error(f"Error recovery failed: {str(e)}")
        raise

async def handle_other_assignment_type(assignment_details: dict, browser: Browser):
    """Handle assignments that are neither quizzes nor Google Docs."""
    try:
        logger.info(f"Handling other assignment type: {assignment_details.get('title')}")
        # Implement the logic for handling other assignment types here
        # For example, download attachments, process text, etc.
    except Exception as e:
        logger.error(f"Error in handle_other_assignment_type: {str(e)}")
        raise
        
        # Check if we're logged out
        if "login" in browser.url.lower():
            await login_to_canvas(GoogleCredentials(email=os.getenv("USERNAME"), password=os.getenv("PASSWORD")), browser)
        
        # If we're on an unexpected page, try to navigate back to the main course page
        course_selector = os.getenv("COURSE_SELECTOR")
        if course_selector not in await browser.title():
            await browser.goto("https://baps.instructure.com/")
            await asyncio.sleep(2)
            course_link = await browser.query_selector(f"a:has-text('{course_selector}')")
            if course_link:
                await course_link.click()
                await browser.wait_for_navigation()
        
        # Try to find and navigate to the correct assignment again
        await navigate_to_correct_assignment(browser, assignment_selector)
        
        logger.info("Error recovery and course correction completed")
    except Exception as e:
        logger.error(f"Failed to recover from error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
