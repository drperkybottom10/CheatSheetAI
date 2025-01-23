from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseAssignment(ABC):
    def __init__(self, assignment_data):
        self.assignment_data = assignment_data

    @abstractmethod
    async def process(self, llm_manager):
        pass

class EssayAssignment(BaseAssignment):
    async def process(self, llm_manager):
        prompt = f"""
        Write an essay on the following topic:
        {self.assignment_data['description']}
        
        Word count: {self.assignment_data.get('word_count', 'Not specified')}
        Due date: {self.assignment_data['due_date']}
        """
        return await llm_manager.generate_response(prompt)

class MultipleChoiceAssignment(BaseAssignment):
    async def process(self, llm_manager):
        prompt = f"""
        Answer the following multiple choice questions:
        {self.assignment_data['description']}
        
        Provide explanations for each answer.
        """
        return await llm_manager.generate_response(prompt)

class ResearchAssignment(BaseAssignment):
    async def process(self, llm_manager):
        prompt = f"""
        Conduct research on the following topic:
        {self.assignment_data['description']}
        
        Provide a detailed report with citations and references.
        Word count: {self.assignment_data.get('word_count', 'Not specified')}
        Due date: {self.assignment_data['due_date']}
        """
        return await llm_manager.generate_response(prompt)

def get_assignment_type(assignment_data):
    assignment_type = assignment_data.get('type', '').lower()
    if 'essay' in assignment_type:
        return EssayAssignment(assignment_data)
    elif 'multiple choice' in assignment_type:
        return MultipleChoiceAssignment(assignment_data)
    elif 'research' in assignment_type:
        return ResearchAssignment(assignment_data)
    else:
        logger.warning(f"Unknown assignment type: {assignment_type}. Defaulting to EssayAssignment.")
        return EssayAssignment(assignment_data)
