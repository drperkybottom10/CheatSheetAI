import asyncio
from browser_use import Browser
from bs4 import BeautifulSoup
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class AssignmentDetails(Dict[str, Any]):
    pass

async def extract_assignment_details(browser: Browser) -> AssignmentDetails:
    try:
        logger.info("Extracting assignment details")
        try:
            # Use the correct method to get page content
            content = await browser.run_javascript("return document.body.innerHTML")
        except AttributeError:
            logger.error("Browser object does not have 'content' method. Falling back to innerHTML.")
            content = await browser.evaluate("document.body.innerHTML")
        soup = BeautifulSoup(content, 'html.parser')
        
        title = soup.find('h1', class_='title')
        description = soup.find('div', class_='description')
        due_date = soup.find('span', class_='due_date')
        completed = soup.find('div', class_='submission_status submitted') is not None
        
        # Add additional logging for debugging missing fields
        allow_recompletion = os.getenv("ALLOW_RECOMPLETION", "False").lower() == "true"
        logger.debug(f"Extracted details: Title={title}, Description={description}, Due Date={due_date}")
        
        return AssignmentDetails({
            "title": title.text.strip() if title else "Unknown Title",
            "description": description.text.strip() if description else "No description available",
            "due_date": due_date.text.strip() if due_date else "No due date specified",
            "links": [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')],
            "completed": completed and not allow_recompletion
        })
    except Exception as e:
        logger.error(f"Failed to extract assignment details: {e}")
        raise
