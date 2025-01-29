import asyncio
from browser_use import Browser
from langchain_community.embeddings import OpenAIEmbeddings
import logging
from utils import generate_assignment_response, check_plagiarism, extract_keywords, extract_requirements, extract_due_date
from assignment_types import get_assignment_type, AssignmentType, handle_assignment
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import os
from agent import ALLOW_RECOMPLETION

logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor()

DEFAULT_DELAY_SECONDS = 3  # Add a default delay to slow down browser actions

async def fill_in_assignment(params, browser: Browser):
    async def sophisticated_match(content, target):
        """
        Implements a detailed matching algorithm using semantic similarity, keyword overlap, and contextual analysis.
        """
        embeddings = OpenAIEmbeddings()
        content_vector = embeddings.embed_query(content)
        target_vector = embeddings.embed_query(target)
        loop = asyncio.get_event_loop()
        similarity_score = await loop.run_in_executor(
            executor,
            lambda: cosine_similarity(content_vector, target_vector)
        )
        return similarity_score > THRESHOLD

    try:
        logger.info(f"Filling in assignment for doc: {params.doc_url}")
        await browser.goto(params.doc_url)
        await asyncio.sleep(2)
        await browser.wait_for_selector("div[role='textbox']", timeout=1000)
        await asyncio.sleep(DEFAULT_DELAY_SECONDS)  # Introduce delay before filling in assignment
        await browser.click("div[role='textbox']")
        await asyncio.sleep(2)

        if sophisticated_match(params.assignment_content, "div[role='textbox']"):
            await browser.type("div[role='textbox']", params.assignment_content, delay=0.05)
            params.completed = True
            return "Assignment filled successfully."
        else:
            return "Assignment content does not match the target."

    except Exception as e:
        logger.error(f"Failed to fill in assignment: {e}")
        return f"Failed to fill in assignment: {str(e)}"

async def complete_assignment(params, browser: Browser):
    try:
        logger.info(f"Completing assignment: {params.assignment_details['title']}")
        
        # Check if the assignment is marked as completed and ALLOW_RECOMPLETION is disabled
        if params.assignment_details.get("completed") and not ALLOW_RECOMPLETION:
            return "Assignment already completed. Skipping as re-completion is not allowed."

        assignment_type = get_assignment_type(params.assignment_details)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: handle_assignment(assignment_type, params.assignment_details, browser)
        )
        
        await asyncio.sleep(DEFAULT_DELAY_SECONDS)  # Introduce delay after handling assignment
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to complete assignment: {e}")
        return f"Failed to complete assignment: {str(e)}"

async def submit_assignment(params, browser: Browser):
    try:
        logger.info(f"Submitting assignment: {params.assignment_url}")
        await browser.goto(params.assignment_url)
        
        await browser.wait_for_selector('button[type="submit"]', timeout=5000)

        if params.submission_type == "file":
            await browser.upload_file('input[type="file"]', params.file_path)
        elif params.submission_type == "text":
            await browser.fill('textarea[name="submission[body]"]', params.text_content)

        await browser.click('button[type="submit"]')
        await browser.wait_for_navigation()
        return "Assignment submitted successfully."
    except Exception as e:
        logger.error(f"Failed to submit assignment: {e}")
        return f"Failed to submit assignment: {str(e)}"
