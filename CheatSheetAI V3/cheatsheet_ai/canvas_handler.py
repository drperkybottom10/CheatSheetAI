import logging

logger = logging.getLogger(__name__)

class CanvasHandler:
    def __init__(self, browser_manager, config):
        self.browser_manager = browser_manager
        self.config = config

    async def login(self):
        page = await self.browser_manager.new_page()
        try:
            await page.goto(f"{self.config.CANVAS_URL}/login")
            await page.fill('input[name="pseudonym_session[unique_id]"]', self.config.CANVAS_USERNAME)
            await page.fill('input[name="pseudonym_session[password]"]', self.config.CANVAS_PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_selector('#dashboard', timeout=10000)
            logger.info("Successfully logged into Canvas")
        except Exception as e:
            logger.error(f"Failed to log into Canvas: {str(e)}")
            raise

    async def navigate_to_course(self):
        page = await self.browser_manager.new_page()
        try:
            await page.goto(f"{self.config.CANVAS_URL}/courses")
            await page.click(f"text={self.config.COURSE_SELECTOR}")
            await page.wait_for_selector('.course-title', timeout=10000)
            logger.info(f"Navigated to course: {self.config.COURSE_SELECTOR}")
        except Exception as e:
            logger.error(f"Failed to navigate to course: {str(e)}")
            raise

    async def navigate_to_assignment(self):
        page = await self.browser_manager.new_page()
        try:
            await page.click('a:text("Assignments")')
            await page.click(f"text={self.config.ASSIGNMENT_SELECTOR}")
            await page.wait_for_selector('.assignment-description', timeout=10000)
            
            assignment_data = {
                'title': await page.text_content('h1.title'),
                'description': await page.text_content('.assignment-description'),
                'due_date': await page.text_content('.date_text'),
                'points': await page.text_content('.points_possible')
            }
            
            logger.info(f"Navigated to assignment: {assignment_data['title']}")
            return assignment_data
        except Exception as e:
            logger.error(f"Failed to navigate to assignment: {str(e)}")
            raise
