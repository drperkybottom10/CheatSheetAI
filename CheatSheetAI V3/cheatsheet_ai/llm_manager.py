import logging
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, config):
        self.config = config
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=self.config.OPENAI_API_KEY
        )

    async def generate_response(self, prompt):
        try:
            response = await self.llm.agenerate([prompt])
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {str(e)}")
            raise
