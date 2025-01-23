import logging
from browser_use import Agent
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class GoogleDocsManager:
    def __init__(self, browser):
        self.browser = browser
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

    async def login(self):
        agent = Agent(
            task="Log into Google account using the provided credentials",
            llm=self.llm,
            browser=self.browser
        )
        history = await agent.run()
        logger.info("Logged into Google successfully" if history.is_done() else "Google login failed")

    async def create_doc(self, title):
        agent = Agent(
            task=f"Create a new Google Doc with the title '{title}'",
            llm=self.llm,
            browser=self.browser
        )
        history = await agent.run()
        return history.extracted_content()

    async def fill_doc(self, doc_url, content):
        agent = Agent(
            task=f"Fill the Google Doc at {doc_url} with the following content: {content}",
            llm=self.llm,
            browser=self.browser
        )
        history = await agent.run()
        logger.info(f"Filled Google Doc: {doc_url}" if history.is_done() else f"Error filling Google Doc: {doc_url}")
