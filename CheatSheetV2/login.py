import asyncio
from browser_use import Browser
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def login_to_canvas(params, browser: Browser, max_retries: int = 3) -> Optional[str]:
    try:
        logger.info("Attempting to log into Canvas.")
        for attempt in range(max_retries):
            try:
                await browser.goto("https://baps.instructure.com/login")
                await browser.wait_for_selector('input[name="pseudonym_session[unique_id]"]', timeout=10000)
                await browser.fill('input[name="pseudonym_session[unique_id]"]', params.email)
                await browser.fill('input[name="pseudonym_session[password]"]', params.password)
                await browser.click('button[type="submit"]')
                await browser.wait_for_navigation()
                
                # Check if login was successful
                if await browser.query_selector('.dashboard-header'):
                    logger.info("Logged into Canvas successfully.")
                    return "Logged into Canvas successfully."
                else:
                    logger.warning(f"Login attempt {attempt + 1} failed. Retrying...")
            except Exception as e:
                logger.error(f"Login attempt {attempt + 1} failed: {str(e)}")
        
        raise Exception("Failed to log in after maximum retries.")
    except Exception as e:
        logger.error(f"Canvas login failed: {e}")
        return f"Canvas login failed: {str(e)}"
