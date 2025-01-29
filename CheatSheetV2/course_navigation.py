import asyncio
from browser_use import Browser
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def search_for_course(course_name: str, browser: Browser) -> Optional[str]:
    try:
        logger.info(f"Searching for course: {course_name}")
        search_input = await browser.wait_for_selector('input[placeholder="Search courses"]', timeout=5000)
        await search_input.fill(course_name)
        await asyncio.sleep(1)  # Wait for search results to populate
        
        course_link = await browser.query_selector(f'a:has-text("{course_name}")')
        if course_link:
            await course_link.click()
            await browser.wait_for_navigation()
            
            # Verify that we're on the correct course page
            course_header = await browser.query_selector('.course-title')
            if course_header and await course_header.inner_text() == course_name:
                return f"Navigated to course: {course_name}"
            else:
                raise Exception("Failed to navigate to the correct course page.")
        raise Exception(f"Course not found: {course_name}")
    except Exception as e:
        logger.error(f"Error searching for course: {str(e)}")
        return None

async def navigate_to_course(course_selector: str, browser: Browser) -> Optional[str]:
    try:
        logger.info(f"Navigating to course: {course_selector}")
        course_link = await browser.wait_for_selector(f"a:has-text('{course_selector}')", timeout=5000)
        await course_link.click()
        await browser.wait_for_navigation()
        
        # Verify that we're on the correct course page
        course_header = await browser.query_selector('.course-title')
        if course_header and course_selector in await course_header.inner_text():
            return f"Navigated to course: {course_selector}"
        else:
            raise Exception("Failed to navigate to the correct course page.")
    except Exception as e:
        logger.error(f"Navigation to course failed: {e}")
        return None
