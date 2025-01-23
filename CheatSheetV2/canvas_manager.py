import logging
from browser_use import Agent
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class CanvasManager:
    def __init__(self, browser):
        self.browser = browser
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

    async def login(self):
        agent = Agent(
            task="Log into Canvas using the provided credentials",
            llm=self.llm,
            browser=self.browser
        )
        history = await agent.run()
        logger.info("Logged into Canvas successfully" if history.is_done() else "Canvas login failed")

    async def get_assignments(self):
        agent = Agent(
            task="Get all assignments from the Canvas dashboard",
            llm=self.llm,
            browser=self.browser
        )
        history = await agent.run()
        return history.extracted_content()

    async def find_assignment(self, assignment_name, class_name):
        browser = await self.browser.new_page()
        try:
            await self.navigate_to_course(class_name)
            assignments = await self.get_assignments()
            for assignment in assignments:
                if assignment_name.lower() in assignment['name'].lower():
                    return assignment
            return None
        except Exception as e:
            logger.error(f"Error finding assignment: {e}")
            raise

    async def navigate_to_course(self, course_selector):
        browser = await self.browser.new_page()
        try:
            await browser.goto("https://baps.instructure.com/courses")
            await browser.click(f"text={course_selector}")
            await browser.wait_for_selector('.course-content')
        except Exception as e:
            logger.error(f"Error navigating to course: {e}")
            raise

    async def navigate_to_assignment(self, assignment_selector):
        browser = await self.browser.new_page()
        try:
            await browser.click(f"text={assignment_selector}")
            await browser.wait_for_selector('.assignment-details')
        except Exception as e:
            logger.error(f"Error navigating to assignment: {e}")
            raise

    async def get_quiz_questions(self, quiz_id):
        browser = await self.browser.new_page()
        try:
            await browser.goto(f"https://baps.instructure.com/courses/current/quizzes/{quiz_id}")
            questions = await browser.evaluate("""
                () => {
                    const questionElements = document.querySelectorAll('.question');
                    return Array.from(questionElements).map(el => ({
                        id: el.dataset.id,
                        text: el.querySelector('.question-text').innerText,
                        options: Array.from(el.querySelectorAll('.answer-option')).map(opt => opt.innerText)
                    }));
                }
            """)
            return questions
        except Exception as e:
            logger.error(f"Error fetching quiz questions: {e}")
            raise

    async def submit_quiz_answers(self, quiz_id, answers):
        browser = await self.browser.new_page()
        try:
            await browser.goto(f"https://baps.instructure.com/courses/current/quizzes/{quiz_id}/take")
            for answer in answers:
                await browser.fill(f"input[name='question_{answer['question_id']}']", answer['answer'])
            await browser.click('button[type="submit"]')
        except Exception as e:
            logger.error(f"Error submitting quiz answers: {e}")
            raise

    async def submit_essay(self, essay_id, content):
        browser = await self.browser.new_page()
        try:
            await browser.goto(f"https://baps.instructure.com/courses/current/assignments/{essay_id}")
            await browser.fill('textarea.submission_body', content)
            await browser.click('button[type="submit"]')
        except Exception as e:
            logger.error(f"Error submitting essay: {e}")
            raise

    async def submit_google_doc(self, assignment_id, doc_url):
        browser = await self.browser.new_page()
        try:
            await browser.goto(f"https://baps.instructure.com/courses/current/assignments/{assignment_id}")
            await browser.fill('input[name="submission[url]"]', doc_url)
            await browser.click('button[type="submit"]')
        except Exception as e:
            logger.error(f"Error submitting Google Doc: {e}")
            raise
