import asyncio
from browser_use import Browser
import logging

logger = logging.getLogger(__name__)

async def create_blank_doc(browser: Browser):
    try:
        await browser.goto("https://docs.google.com/document/create")
        await browser.wait_for_selector('div[role="textbox"]', timeout=5000)
        return "Blank Google Doc created successfully."
    except Exception as e:
        logger.error(f"Failed to create blank Google Doc: {e}")
        return f"Failed to create blank Google Doc: {str(e)}"

async def make_copy_of_google_doc(params, browser: Browser):
    try:
        await browser.goto(params.original_url)
        await browser.wait_for_selector('div[role="textbox"]', timeout=10000)
        
        # Use keyboard shortcuts to make a copy
        await browser.keyboard.press('Alt+F')
        await browser.keyboard.press('M')
        await browser.wait_for_selector('input[aria-label="Copy document"]', timeout=10000)
        
        # Wait for the new document to load
        await browser.wait_for_navigation()
        await asyncio.sleep(5)

        if params.new_title:
            await browser.fill('input[aria-label="Copy document"]', params.new_title)
        
        await browser.click('button:text("OK")')
        await browser.wait_for_navigation()
        
        new_doc_url = browser.url
        logger.info(f"New document created: {new_doc_url}")
        return new_doc_url
    except Exception as e:
        logger.error(f"Failed to make a copy of Google Doc: {e}")
        return f"Failed to make a copy of Google Doc: {str(e)}"

async def filter_google_docs_links(links):
    return [link for link in links if "docs.google.com" in link]

async def handle_google_doc(doc, browser: Browser):
    try:
        await browser.goto(doc.url)
        await browser.wait_for_selector('div[role="textbox"]', timeout=5000)
        return "Google Doc opened successfully."
    except Exception as e:
        logger.error(f"Failed to handle Google Doc: {e}")
        return f"Failed to handle Google Doc: {str(e)}"
