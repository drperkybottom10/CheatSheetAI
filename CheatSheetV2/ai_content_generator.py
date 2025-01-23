import logging
from langchain_google_vertexai import ChatVertexAI
from typing import List, Dict

logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatVertexAI(
            model="gemini-1.5-flash",
            temperature=0.3
        )

    async def generate_content(self, prompt: str, assignment_type: str, requirements: List[str]) -> str:
        try:
            full_prompt = self._create_full_prompt(prompt, assignment_type, requirements)
            response = await self.llm.agenerate([full_prompt])
            return response.generations[0].text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def _create_full_prompt(self, prompt: str, assignment_type: str, requirements: List[str]) -> str:
        return f"""
        Assignment Type: {assignment_type}
        Requirements:
        {' '.join(f'- {req}' for req in requirements)}

        Task: {prompt}

        Please complete the assignment based on the given information. Ensure that the response:
        1. Fully addresses the task and meets all requirements
        2. Is written in a natural, human-like style
        3. Avoids obvious patterns or structures that might be detected as AI-generated
        4. Includes relevant examples, anecdotes, or personal experiences where appropriate
        5. Uses varied sentence structures and vocabulary
        6. Maintains a consistent tone and style throughout

        Response:
        """

    async def rephrase_content(self, content: str) -> str:
        rephrase_prompt = f"""
        Please rephrase the following content to make it more natural and less likely to be detected as AI-generated:

        {content}

        Ensure the rephrased version:
        1. Maintains the same meaning and key points
        2. Uses varied sentence structures and vocabulary
        3. Includes natural language patterns and transitions
        4. Avoids obvious repetition or formulaic writing
        """
        try:
            response = await self.llm.agenerate([rephrase_prompt])
            return response.generations[0].text
        except Exception as e:
            logger.error(f"Error rephrasing content: {e}")
            raise

    async def generate_quiz_answers(self, questions: List[Dict[str, str]]) -> List[Dict[str, str]]:
        answers = []
        for question in questions:
            prompt = f"""
            Question: {question['text']}
            Options: {', '.join(question['options'])}

            Please provide the correct answer to this question, along with a brief explanation that sounds natural and student-like. Ensure the response:
            1. Clearly states the correct answer
            2. Provides a concise explanation
            3. Uses language that a student would typically use
            4. Avoids overly technical or perfect-sounding explanations
            """
            try:
                response = await self.llm.agenerate([prompt])
                answers.append({
                    'question_id': question['id'],
                    'answer': response.generations[0].text
                })
            except Exception as e:
                logger.error(f"Error generating quiz answer: {e}")
                raise
        return answers
