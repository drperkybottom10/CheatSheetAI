import logging
from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt):
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=config.OPENAI_API_KEY
        )

    async def generate_response(self, prompt):
        try:
            response = await self.llm.agenerate([prompt])
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"Failed to generate OpenAI response: {str(e)}")
            raise

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config):
        self.llm = ChatAnthropic(
            model="claude-2",
            temperature=0.7,
            anthropic_api_key=config.ANTHROPIC_API_KEY
        )

    async def generate_response(self, prompt):
        try:
            response = await self.llm.agenerate([prompt])
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"Failed to generate Anthropic response: {str(e)}")
            raise

def get_llm_provider(provider_name, config):
    if provider_name.lower() == 'openai':
        return OpenAIProvider(config)
    elif provider_name.lower() == 'anthropic':
        return AnthropicProvider(config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
