from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, BrowserConfig, Browser
from browser_use.browser.context import BrowserContextConfig
from browser_use.controller.service import Controller
import asyncio
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional, List
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize browser configuration with headless mode for speed
browser_config = BrowserConfig(
    headless=False,  # Enable headless mode for faster execution
    disable_security=True,
    extra_chromium_args=[
        '--disable-blink-features=AutomationControlled',
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

# Initialize the LLM with optimized settings
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-002",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3  # Removed deprecated parameter
)

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

class DocumentCopyDetails(BaseModel):
    original_url: str
    new_title: Optional[str] = None

class FillAssignmentDetails(BaseModel):
    doc_url: str
    assignment_content: str

# Initialize controller
controller = Controller()

# Register custom actions with optimized implementations
@controller.action("Login to Canvas", requires_browser=True)
async def login_to_canvas(params: GoogleCredentials, browser: Browser):
    try:
        logger.info("Attempting to log into Canvas.")
        await browser.goto("https://baps.instructure.com/login")
        await browser.fill('input[name="pseudonym_session[unique_id]"]', params.email)
        await browser.fill('input[name="pseudonym_session[password]"]', params.password)
        await browser.click('button[name="submit"]')
        await browser.wait_for_selector('selector-for-dashboard', timeout=1000)  # FASTER
        return "Logged into Canvas successfully."
    except Exception as e:
        logger.error(f"Canvas login failed: {e}")
        return f"Canvas login failed: {str(e)}"

@controller.action("Navigate to Course", requires_browser=True)
async def navigate_to_course(course_selector: str, browser: Browser):
    try:
        logger.info(f"Navigating to course: {course_selector}")
        await browser.wait_for_selector(f"text='{course_selector}'", timeout=1000)  # FASTER
        await browser.click(f"text='{course_selector}'")
        await browser.wait_for_selector('selector-for-course-page', timeout=1000)   # FASTER
        return f"Navigated to course: {course_selector}"
    except Exception as e:
        logger.error(f"Navigation to course failed: {e}")
        return f"Navigation to course failed: {str(e)}"

@controller.action("Navigate to Assignment", requires_browser=True)
async def navigate_to_assignment(assignment_selector: str, browser: Browser):
    try:
        logger.info(f"Navigating to assignment: {assignment_selector}")
        await browser.wait_for_selector(f"text='{assignment_selector}'", timeout=1000)  # FASTER
        await browser.click(f"text='{assignment_selector}'")
        await browser.wait_for_selector('selector-for-assignment-page', timeout=1000)   # FASTER
        return f"Navigated to assignment: {assignment_selector}"
    except Exception as e:
        logger.error(f"Navigation to assignment failed: {e}")
        return f"Navigation to assignment failed: {str(e)}"

@controller.action("Extract Assignment Details", requires_browser=True)
async def extract_assignment_details(browser: Browser) -> AssignmentData:
    try:
        logger.info("Extracting assignment details.")
        description = await browser.evaluate('document.querySelector(".description").innerText')
        instructions = await browser.evaluate('document.querySelector(".instructions").innerText')
        links = await browser.evaluate('Array.from(document.querySelectorAll("a")).map(a => a.href)')
        attachments = await browser.evaluate('Array.from(document.querySelectorAll("a.download")).map(a => a.href)')
        return AssignmentData(
            description=description,
            instructions=instructions,
            links=links,
            attachments=attachments
        )
    except Exception as e:
        logger.error(f"Failed to extract assignment details: {e}")
        return AssignmentData(description="", instructions="", links=[], attachments=[])

@controller.action("Filter Google Docs Links", requires_browser=True)
async def filter_google_docs_links(links: List[str]) -> List[str]:
    google_docs_links = [link for link in links if "docs.google.com/document" in link]
    return google_docs_links

@controller.action("Login to Google", param_model=GoogleCredentials, requires_browser=True)
async def login_to_google(params: GoogleCredentials, browser: Browser):
    try:
        logger.info("Attempting to log into Google.")
        await browser.goto("https://accounts.google.com/signin")
        await browser.fill('input[type="email"]', params.email)
        await browser.click('button[jsname="LgbsSe"]')
        await browser.wait_for_selector('input[type="password"]', timeout=5000)  # Wait for password field
        await browser.fill('input[type="password"]', params.password)
        await browser.click('button[jsname="LgbsSe"]')
        await browser.wait_for_selector('selector-for-logged-in-state', timeout=5000)  # Event-based wait
        return "Successfully logged into Google"
    except Exception as e:
        logger.error(f"Google login failed: {e}")
        return f"Login failed: {str(e)}"

@controller.action("Log out of Google", requires_browser=True)
async def logout_of_google(browser: Browser):
    try:
        logger.info("Logging out of Google.")
        await browser.goto("https://accounts.google.com/Logout")
        await browser.wait_for_selector('selector-for-logged-out-state', timeout=5000)  # Event-based wait
        return "Logged out of Google successfully."
    except Exception as e:
        logger.error(f"An error occurred during Google logout: {e}")
        return f"An error occurred during Google logout: {str(e)}"

@controller.action("Make a copy of Google Doc", param_model=DocumentCopyDetails, requires_browser=True)
async def make_copy_of_google_doc(params: DocumentCopyDetails, browser: Browser):
    try:
        logger.info(f"Making a copy of Google Doc: {params.original_url}")
        copy_url = f"{params.original_url}/copy"
        await browser.goto(copy_url)
        if params.new_title:
            await browser.fill('input[name="title"]', params.new_title)
        await browser.click('button[jsname="LgbsSe"]')  # Click "OK" to make a copy
        await browser.wait_for_selector('selector-for-new-doc', timeout=5000)  # Event-based wait
        new_doc_url = browser.url
        return new_doc_url
    except Exception as e:
        logger.error(f"Failed to make a copy: {e}")
        return f"Failed to make a copy: {str(e)}"

@controller.action("Fill in assignment", param_model=FillAssignmentDetails, requires_browser=True)
async def fill_in_assignment(params: FillAssignmentDetails, browser: Browser):
    try:
        logger.info(f"Filling in assignment for doc: {params.doc_url}")
        await browser.goto(params.doc_url)
        await browser.wait_for_selector("div[role='textbox']", timeout=1000)  # FASTER
        await browser.click("div[role='textbox']")
        await browser.type("div[role='textbox']", params.assignment_content, delay=0.01)  # FASTER
        return "Assignment filled successfully."
    except Exception as e:
        logger.error(f"Failed to fill in assignment: {e}")
        return f"Failed to fill in assignment: {str(e)}"

@controller.action("Open new tab", requires_browser=True)
async def open_new_tab(browser: Browser):
    try:
        logger.info("Opening a new tab.")
        new_page = await browser.context.new_page()
        await new_page.bring_to_front()
        return "Opened a new tab successfully."
    except Exception as e:
        logger.error(f"Failed to open new tab: {e}")
        return f"Failed to open new tab: {str(e)}"

@controller.action("Create blank doc", requires_browser=True)
async def create_blank_doc(browser: Browser):
    try:
        logger.info("Creating a new blank Google Doc.")
        new_page = await browser.context.new_page()
        await new_page.bring_to_front()
        await new_page.goto("https://docs.google.com/document/create")
        await new_page.wait_for_selector("div[role='textbox']", timeout=5000)
        return "Created a new blank Google Doc successfully."
    except Exception as e:
        logger.error(f"Error creating new blank doc: {e}")
        return f"Error creating new blank doc: {str(e)}"

@controller.action("Close error popup", requires_browser=True)
async def close_error_popup(browser: Browser):
    try:
        logger.info("Closing error popup.")
        await browser.click('button[aria-label="Close"]')
        return "Successfully closed error popup."
    except Exception as e:
        logger.error(f"Failed to close error popup: {e}")
        return f"Failed to close error popup: {str(e)}"

@controller.action("Handle Google Doc", param_model=DocumentDetails, requires_browser=True)
async def handle_google_doc(params: DocumentDetails, browser: Browser):
    try:
        logger.info(f"Handling Google Doc: {params.url}")
        if params.url:
            await browser.goto(params.url)
        await browser.wait_for_selector("div[role='textbox']", timeout=5000)
        content = await browser.evaluate('document.querySelector("div[role=\'textbox\']").innerText')
        return DocumentDetails(
            url=params.url,
            content=content,
            is_assignment=params.is_assignment
        )
    except Exception as e:
        logger.error(f"Failed to handle Google Doc: {e}")
        return DocumentDetails(url=params.url, content="", is_assignment=False)

@controller.action("Navigate Google Doc", param_model=DocumentDetails, requires_browser=True)
async def navigate_google_doc(params: DocumentDetails, browser: Browser):
    try:
        logger.info("Navigating Google Doc.")
        # Add keyboard shortcuts for navigation
        await browser.keyboard.press("Control+Home")  # Go to start
        await browser.keyboard.press("Control+A")     # Select all
        await browser.keyboard.press("Control+C")     # Copy content
        
        # Extract text content more reliably
        content = await browser.evaluate("""
            () => {
                const textboxes = document.querySelectorAll('div[role="textbox"]');
                return Array.from(textboxes).map(box => box.innerText).join('\\n');
            }
        """)
        
        # Parse document structure
        sections = await browser.evaluate("""
            () => {
                const headers = document.querySelectorAll('[role="heading"]');
                return Array.from(headers).map(h => ({
                    text: h.innerText,
                    level: h.getAttribute('aria-level')
                }));
            }
        """)
        
        return DocumentDetails(content=content, structure=sections)
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        return f"Navigation failed: {str(e)}"

@controller.action("Analyze Assignment", param_model=AssignmentData, requires_browser=True)
async def analyze_assignment(params: AssignmentData, browser: Browser):
    try:
        logger.info("Analyzing assignment.")
        instructions = await browser.evaluate("""
            () => {
                const instructionBlocks = document.querySelectorAll('.assignment-description p');
                return Array.from(instructionBlocks).map(p => p.innerText);
            }
        """)
        requirements = await browser.evaluate("""
            () => {
                const lists = document.querySelectorAll('ul, ol');
                return Array.from(lists).map(list =>
                    Array.from(list.children).map(item => item.innerText)
                );
            }
        """)
        
        return {
            'instructions': instructions,
            'requirements': requirements
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return f"Analysis failed: {str(e)}"

@controller.action("Interact with Doc", requires_browser=True)
async def interact_with_doc(browser: Browser):
    try:
        logger.info("Interacting with Google Doc.")
        # Use more precise selectors
        await browser.evaluate("""
            () => {
                // Focus on editable area
                const textbox = document.querySelector('div[role="textbox"]');
                if (textbox) {
                    textbox.focus();
                }
                
                // Set cursor position
                const selection = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(textbox);
                selection.removeAllRanges();
                selection.addRange(range);
            }
        """)
        
        # Support rich text editing
        await browser.keyboard.type('/heading')  # Google Docs command menu
        await browser.keyboard.press('Enter');
        
        return "Document interaction successful"
    except Exception as e:
        logger.error(f"Interaction failed: {e}")
        return f"Interaction failed: {str(e)}"

@controller.action("Mouse Navigation", requires_browser=True)
async def mouse_navigation(browser: Browser):
    try:
        logger.info("Performing mouse navigation.")
        # Get viewport size
        viewport = await browser.evaluate('() => ({width: window.innerWidth, height: window.innerHeight})')
        
        # Smooth mouse movement
        await browser.mouse.move(viewport['width']/2, viewport['height']/2, steps=5)
        await browser.mouse.down()
        await browser.mouse.move(viewport['width']/2, viewport['height']/2 + 100, steps=5)
        await browser.mouse.up()
        
        return "Mouse navigation completed"
    except Exception as e:
        logger.error(f"Mouse navigation failed: {e}")
        return f"Mouse navigation failed: {str(e)}"

# Add a new environment variable for quiz access code
quiz_access_code = os.getenv("QUIZ_ACCESS_CODE")

@controller.action("Take Canvas Quiz", requires_browser=True)
async def take_canvas_quiz(browser: Browser):
    """
    Reads each quiz question, optionally enters the quiz access code,
    then selects the answer. Adjust DOM selectors and logic as needed.
    """
    try:
        logger.info("Taking Canvas quiz.")
        # If a quiz access code is required, fill it in before proceeding
        if quiz_access_code:
            await browser.wait_for_selector('.quiz-access-code', timeout=5000)
            await browser.fill('.quiz-access-code', quiz_access_code)
            await browser.click('button.submit-access-code')
            await browser.wait_for_selector('.quiz-container', timeout=5000)

        # Wait for quiz container
        await browser.wait_for_selector('.quiz-container', timeout=5000)

        # Example: find all questions
        question_selectors = await browser.evaluate('Array.from(document.querySelectorAll(".quiz-question")).map((el, idx) => `.quiz-question:nth-of-type(${idx + 1})`)')
        for question_sel in question_selectors:
            question_text = await browser.evaluate(f'document.querySelector("{question_sel} .question-text").innerText')
            # Placeholder "correct" answer logic (replace with your actual method)
            possible_answers = await browser.evaluate(f'Array.from(document.querySelectorAll("{question_sel} .answer-option")).map(a => a.innerText)')
            
            # Simple example: picks the first answer
            if possible_answers:
                await browser.click(f'{question_sel} .answer-option input[type="radio"]')

        # Submit quiz (update selector to match your layout)
        await browser.click('button.submit-quiz')
        await browser.wait_for_selector('.quiz-complete', timeout=5000)
        return "Quiz completed."
    except Exception as e:
        logger.error(f"Failed to complete quiz: {e}")
        return f"Failed to complete quiz: {str(e)}"

async def run_agent_task(agent_task: str, llm: ChatGoogleGenerativeAI, controller: Controller, browser: Browser):
    agent = Agent(
        task=agent_task,
        llm=llm,
        controller=controller,  # Corrected typo
        use_vision=True,
        save_conversation_path="logs/conversation.json",
        browser=browser
    )
    return await agent.run()

async def main():
    try:
        # Validate environment variables
        required_env_vars = [
            "USERNAME", "PASSWORD", "COURSE_SELECTOR",
            "ASSIGNMENT_SELECTOR", "GOOGLE_EMAIL",
            "GOOGLE_PASSWORD", "PROVIDED_GOOGLE_DOC_URL"
        ]

        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Get environment variables
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        course_selector = os.getenv("COURSE_SELECTOR")
        assignment_selector = os.getenv("ASSIGNMENT_SELECTOR")
        google_email = os.getenv("GOOGLE_EMAIL")
        google_password = os.getenv("GOOGLE_PASSWORD")
        provided_google_doc_url = os.getenv("PROVIDED_GOOGLE_DOC_URL")

        # Initialize Browser with config
        browser = Browser(config=browser_config)

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
        """

        # Run the main agent task
        main_result = await run_agent_task(main_task, llm, controller, browser)
        print(main_result)

        # Extract Google Docs links from the assignment details
        doc_links = await filter_google_docs_links((await extract_assignment_details(browser)).links)

        if not doc_links and provided_google_doc_url:
            # Open provided Google Doc
            await handle_google_doc(DocumentDetails(url=provided_google_doc_url), browser)
            new_doc_url = await make_copy_of_google_doc(DocumentCopyDetails(original_url=provided_google_doc_url, new_title="Copied Assignment"), browser)
            if new_doc_url.startswith("http"):
                fill_result = await fill_in_assignment(FillAssignmentDetails(doc_url=new_doc_url, assignment_content="Completed assignment content here..."), browser)
                print(fill_result)
        elif doc_links:
            # Run agents concurrently for each Google Doc link
            copy_tasks = [
                make_copy_of_google_doc(DocumentCopyDetails(original_url=link, new_title="Copied Assignment"), browser) for link in doc_links
            ]
            copied_docs = await asyncio.gather(*copy_tasks)

            fill_tasks = []
            for new_doc_url in copied_docs:
                if new_doc_url.startswith("http"):
                    fill_tasks.append(fill_in_assignment(FillAssignmentDetails(doc_url=new_doc_url, assignment_content="Completed assignment content here..."), browser))
                else:
                    print(new_doc_url)  # Error message

            fill_results = await asyncio.gather(*fill_tasks)
            for result in fill_results:
                print(result)
        else:
            # No links and no provided doc, create a new blank doc
            create_result = await create_blank_doc(browser)
            print(create_result)

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    finally:
        # Ensure the browser is closed even if an error occurs
        if 'browser' in locals():
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())