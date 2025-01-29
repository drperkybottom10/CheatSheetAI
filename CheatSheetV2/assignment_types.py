import asyncio
from enum import Enum
from browser_use import Browser
import logging
import os
from utils import generate_assignment_response
from agent import ALLOW_RECOMPLETION

logger = logging.getLogger(__name__)

class AssignmentType(Enum):
    QUIZ = "quiz"
    WRITING = "writing"
    ANNOTATED_BIBLIOGRAPHY = "annotated_bibliography"
    REFLECTIVE_JOURNAL = "reflective_journal"
    CASE_STUDY = "case_study"
    GENERAL_REASONING = "general_reasoning"
    FILE_UPLOAD = "file_upload"
    DISCUSSION = "discussion"
    PEER_REVIEW = "peer_review"
    GROUP_PROJECT = "group_project"
    PRESENTATION = "presentation"
    LAB_REPORT = "lab_report"
    PROBLEM_SET = "problem_set"
    UNKNOWN = "unknown"

def get_assignment_type(assignment_details):
    description = assignment_details['description'].lower()
    title = assignment_details['title'].lower()

    if "quiz" in description or "quiz" in title:
        return AssignmentType.QUIZ
    elif any(keyword in description for keyword in ["write", "essay", "paragraph"]):
        return AssignmentType.WRITING
    elif "annotated bibliography" in description or "citation analysis" in description:
        return AssignmentType.ANNOTATED_BIBLIOGRAPHY
    elif "reflective journal" in description or "personal reflection" in description:
        return AssignmentType.REFLECTIVE_JOURNAL
    elif "case study" in description or "analysis" in description:
        return AssignmentType.CASE_STUDY
    elif "general reasoning" in description or "fallback" in description:
        return AssignmentType.GENERAL_REASONING
    elif "file upload" in description:
        return AssignmentType.FILE_UPLOAD
    elif "discussion" in description or "forum" in description:
        return AssignmentType.DISCUSSION
    elif "peer review" in description:
        return AssignmentType.PEER_REVIEW
    elif "group project" in description or "team assignment" in description:
        return AssignmentType.GROUP_PROJECT
    elif "presentation" in description or "slideshow" in description:
        return AssignmentType.PRESENTATION
    elif "lab report" in description:
        return AssignmentType.LAB_REPORT
    elif "problem set" in description or "worksheet" in description:
        return AssignmentType.PROBLEM_SET
    else:
        return AssignmentType.UNKNOWN

async def handle_assignment(assignment_type, assignment_details, browser: Browser):
    handlers = {
        AssignmentType.QUIZ: handle_quiz,
        AssignmentType.WRITING: handle_writing_assignment,
        AssignmentType.ANNOTATED_BIBLIOGRAPHY: handle_annotated_bibliography,
        AssignmentType.REFLECTIVE_JOURNAL: handle_reflective_journal,
        AssignmentType.CASE_STUDY: handle_case_study,
        AssignmentType.GENERAL_REASONING: handle_general_reasoning,
        AssignmentType.FILE_UPLOAD: handle_file_upload_assignment,
        AssignmentType.DISCUSSION: handle_discussion,
        AssignmentType.PEER_REVIEW: handle_peer_review,
        AssignmentType.GROUP_PROJECT: handle_group_project,
        AssignmentType.PRESENTATION: handle_presentation,
        AssignmentType.LAB_REPORT: handle_lab_report,
        AssignmentType.PROBLEM_SET: handle_problem_set,
        AssignmentType.UNKNOWN: handle_unknown_assignment
    }

    handler = handlers.get(assignment_type, handle_unknown_assignment)
    return await handler(assignment_details, browser)

async def handle_quiz(assignment_details, browser: Browser):
    try:
        logger.info("Handling quiz")
        
        # Check if the quiz is already completed and ALLOW_RECOMPLETION is disabled
        if assignment_details.get("completed") and not ALLOW_RECOMPLETION:
            logger.info("Quiz already completed. Skipping as re-completion is not allowed.")
            return "Quiz already completed. Skipping as re-completion is not allowed."
        
        # If ALLOW_RECOMPLETION is enabled, we'll proceed with the quiz regardless of its completion status
        start_button = await browser.query_selector('button:has-text("Start Quiz")')
        resume_button = await browser.query_selector('button:has-text("Resume Quiz")')
        if start_button:
            await start_button.click()
        elif resume_button:
            await resume_button.click()
        
        # Check for access code
        access_code_input = await browser.query_selector('input[placeholder="Access Code"]')
        if access_code_input:
            access_code = os.getenv("QUIZ_ACCESS_CODE")
            await access_code_input.fill(access_code)
            submit_code_button = await browser.query_selector('button:has-text("Submit")')
            if submit_code_button:
                await submit_code_button.click()
        
        # Scroll through the entire quiz to load all questions
        await browser.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)  # Wait for content to load
        
        questions = await browser.query_selector_all('.question')
        
        for question in questions:
            # Scroll the question into view
            await question.scroll_into_view_if_needed()
            await asyncio.sleep(1)  # Wait for any dynamic content to load
            
            question_text = await question.evaluate('(el) => el.textContent')
            answer = await generate_assignment_response(f"Quiz question: {question_text}")
            
            # Handle different question types
            if await question.query_selector('input[type="text"]'):
                await question.fill('input[type="text"]', answer)
            elif await question.query_selector('input[type="radio"]'):
                options = await question.query_selector_all('input[type="radio"]')
                best_option = await find_best_option(options, answer)
                if best_option:
                    await best_option.click()
            elif await question.query_selector('textarea'):
                await question.fill('textarea', answer)
            # Scroll down after answering each question
            await browser.evaluate("window.scrollBy(0, 200)")
        
        submit_button = await browser.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            await browser.wait_for_navigation()

        return "Quiz completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete quiz: {e}")
        return f"Failed to complete quiz: {str(e)}"

async def find_best_option(options, answer):
    best_option = None
    best_match = 0
    for option in options:
        option_text = await option.evaluate('(el) => el.nextSibling.textContent')
        match_score = calculate_match_score(option_text, answer)
        if match_score > best_match:
            best_match = match_score
            best_option = option
    return best_option

def calculate_match_score(option_text, answer):
    # Implement a simple matching algorithm
    # This is a placeholder and should be replaced with a more sophisticated method
    return len(set(option_text.lower().split()) & set(answer.lower().split()))

async def handle_writing_assignment(assignment_details, browser: Browser):
    try:
        logger.info("Handling writing assignment")
        content = await generate_assignment_response(f"Writing assignment: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="submission[body]"]')
        if text_area:
            await text_area.fill(content)
        return "Writing assignment completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete writing assignment: {e}")
        return f"Failed to complete writing assignment: {str(e)}"

async def handle_annotated_bibliography(assignment_details, browser: Browser):
    try:
        logger.info("Handling annotated bibliography assignment")
        content = await generate_assignment_response(f"Create an annotated bibliography for: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="submission[body]"]')
        if text_area:
            await text_area.fill(content)
        return "Annotated bibliography completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete annotated bibliography: {e}")
        return f"Failed to complete annotated bibliography: {str(e)}"

async def handle_reflective_journal(assignment_details, browser: Browser):
    try:
        logger.info("Handling reflective journal assignment")
        content = await generate_assignment_response(f"Write a reflective journal for: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="submission[body]"]')
        if text_area:
            await text_area.fill(content)
        return "Reflective journal completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete reflective journal: {e}")
        return f"Failed to complete reflective journal: {str(e)}"

async def handle_case_study(assignment_details, browser: Browser):
    try:
        logger.info("Handling case study assignment")
        content = await generate_assignment_response(f"Analyze the case study: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="submission[body]"]')
        if text_area:
            await text_area.fill(content)
        return "Case study completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete case study: {e}")
        return f"Failed to complete case study: {str(e)}"

async def handle_general_reasoning(assignment_details, browser: Browser):
    try:
        logger.info("Handling general reasoning assignment")
        content = await generate_assignment_response(f"Analyze and complete the following assignment using agentic reasoning: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="submission[body]"]')
        if text_area:
            await text_area.fill(content)
        return "General reasoning assignment completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete general reasoning assignment: {e}")
        return f"Failed to complete general reasoning assignment: {str(e)}"

async def handle_file_upload_assignment(assignment_details, browser: Browser):
    try:
        logger.info("Handling file upload assignment")
        content = await generate_assignment_response(f"File upload assignment: {assignment_details['description']}")
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        file_input = await browser.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(temp_file_path)
        
        import os
        os.unlink(temp_file_path)
        
        return "File upload assignment completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete file upload assignment: {e}")
        return f"Failed to complete file upload assignment: {str(e)}"

async def handle_discussion(assignment_details, browser: Browser):
    try:
        logger.info("Handling discussion assignment")
        content = await generate_assignment_response(f"Discussion assignment: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="message"]')
        if text_area:
            await text_area.fill(content)
        post_button = await browser.query_selector('button[type="submit"]')
        if post_button:
            await post_button.click()
        return "Discussion post completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete discussion assignment: {e}")
        return f"Failed to complete discussion assignment: {str(e)}"

async def handle_peer_review(assignment_details, browser: Browser):
    try:
        logger.info("Handling peer review assignment")
        review_content = await generate_assignment_response(f"Write a peer review for: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="review_comment"]')
        if text_area:
            await text_area.fill(review_content)
        submit_button = await browser.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.click()
        return "Peer review completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete peer review assignment: {e}")
        return f"Failed to complete peer review assignment: {str(e)}"

async def handle_group_project(assignment_details, browser: Browser):
    try:
        logger.info("Handling group project assignment")
        project_content = await generate_assignment_response(f"Create a project plan for: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="group_submission"]')
        if text_area:
            await text_area.fill(project_content)
        submit_button = await browser.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.click()
        return "Group project submission completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete group project assignment: {e}")
        return f"Failed to complete group project assignment: {str(e)}"

async def handle_presentation(assignment_details, browser: Browser):
    try:
        logger.info("Handling presentation assignment")
        presentation_content = await generate_assignment_response(f"Create a presentation outline for: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="presentation_notes"]')
        if text_area:
            await text_area.fill(presentation_content)
        submit_button = await browser.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.click()
        return "Presentation assignment completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete presentation assignment: {e}")
        return f"Failed to complete presentation assignment: {str(e)}"

async def handle_lab_report(assignment_details, browser: Browser):
    try:
        logger.info("Handling lab report assignment")
        report_content = await generate_assignment_response(f"Write a lab report for: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="lab_report"]')
        if text_area:
            await text_area.fill(report_content)
        submit_button = await browser.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.click()
        return "Lab report completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete lab report assignment: {e}")
        return f"Failed to complete lab report assignment: {str(e)}"

async def handle_problem_set(assignment_details, browser: Browser):
    try:
        logger.info("Handling problem set assignment")
        solutions = await generate_assignment_response(f"Solve the problem set: {assignment_details['description']}")
        text_area = await browser.query_selector('textarea[name="problem_set_solutions"]')
        if text_area:
            await text_area.fill(solutions)
        submit_button = await browser.query_selector('button[type="submit"]')
        if submit_button:
            await submit_button.click()
        return "Problem set completed successfully."
    except Exception as e:
        logger.error(f"Failed to complete problem set assignment: {e}")
        return f"Failed to complete problem set assignment: {str(e)}"

async def handle_unknown_assignment(assignment_details, browser: Browser):
    logger.warning(f"Unknown assignment type: {assignment_details['title']}")
    return "Unable to determine assignment type. Please complete manually."
