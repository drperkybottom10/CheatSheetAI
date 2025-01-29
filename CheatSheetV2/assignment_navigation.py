import asyncio
from browser_use import Browser
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_DELAY_SECONDS = 2  # Reduced delay for faster execution

async def search_for_assignment(params, browser: Browser):
    # Introduce delay before searching for assignment
    await asyncio.sleep(DEFAULT_DELAY_SECONDS)
    try:
        logger.info(f"Searching for assignment: {params.assignment_name}")
        await browser.wait_for_selector('input[placeholder="Search assignments"]', timeout=5000)
        search_input = await browser.query_selector('input[placeholder="Search assignments"]')
        await search_input.fill(params.assignment_name)
        await asyncio.sleep(2)
        
        # Use a more flexible selector to find the assignment link
        assignment_link = await browser.query_selector(f'a:has-text("{params.assignment_name}")', timeout=5000)
        if assignment_link:
            await assignment_link.click()
            await browser.wait_for_navigation()
            
            # Verify that we're on the correct assignment page
            page_title = await browser.title()
            if params.assignment_name.lower() not in page_title.lower():
                logger.warning(f"Navigated to incorrect assignment: {page_title}")
                return None
            
        logger.warning(f"Assignment not found: {params.assignment_name}")
        return None
    except Exception as e:
        logger.error(f"Error searching for assignment: {str(e)}")
        return None

async def navigate_to_assignment(params, browser: Browser) -> Optional[str]:
    try:
        logger.info(f"Navigating to assignment: {params.assignment_selector}")
        
        # Scroll the page to ensure all assignments are loaded
        await browser.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        
        # Try to find the assignment link
        assignment_link = await browser.query_selector(f"a:has-text('{params.assignment_selector}')", timeout=5000)
        if assignment_link:
            await assignment_link.click()
            await browser.wait_for_navigation()
            
            # Verify that we're on the correct assignment page
            page_title = await browser.title()
            if params.assignment_selector.lower() not in page_title.lower():
                logger.warning(f"Navigated to incorrect assignment: {page_title}")
                return None
            
            return f"Navigated to assignment: {params.assignment_selector}"
        else:
            logger.warning(f"Assignment not found: {params.assignment_selector}")
            return None
    except Exception as e:
        logger.error(f"Navigation to assignment failed: {e}")
        return None
