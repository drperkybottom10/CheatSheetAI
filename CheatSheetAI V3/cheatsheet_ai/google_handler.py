import logging

logger = logging.getLogger(__name__)

class GoogleHandler:
    def __init__(self, browser_manager, config):
        self.browser_manager = browser_manager
        self.config = config

    async def login(self):
        page = await self.browser_manager.new_page()
        try:
            await page.goto("https://accounts.google.com/signin")
            await page.fill('input[type="email"]', self.config.GOOGLE_EMAIL)
            await page.click('button:has-text("Next")')
            await page.fill('input[type="password"]', self.config.GOOGLE_PASSWORD)
            await page.click('button:has-text("Next")')
            await page.wait_for_selector('a[aria-label="Google apps"]', timeout=10000)
            logger.info("Successfully logged into Google")
        except Exception as e:
            logger.error(f"Failed to log into Google: {str(e)}")
            raise

    async def create_or_copy_document(self, title):
        page = await self.browser_manager.new_page()
        try:
            await page.goto(f"{self.config.GOOGLE_DOCS_URL}/create")
            await page.wait_for_selector('.docs-title-input', timeout=10000)
            await page.fill('.docs-title-input', title)
            doc_url = page.url
            logger.info(f"Created new Google Doc: {doc_url}")
            return doc_url
        except Exception as e:
            logger.error(f"Failed to create Google Doc: {str(e)}")
            raise

    async def fill_document(self, doc_url, content):
        page = await self.browser_manager.new_page()
        try:
            await page.goto(doc_url)
            await page.wait_for_selector('.kix-appview-editor', timeout=10000)
            await page.keyboard.type(content)
            logger.info(f"Filled content in Google Doc: {doc_url}")
        except Exception as e:
            logger.error(f"Failed to fill Google Doc: {str(e)}")
            raise
