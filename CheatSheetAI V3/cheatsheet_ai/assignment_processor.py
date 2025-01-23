import logging

logger = logging.getLogger(__name__)

class AssignmentProcessor:
    def __init__(self, llm_manager, config):
        self.llm_manager = llm_manager
        self.config = config

    async def process(self, assignment_data):
        try:
            prompt = self._create_prompt(assignment_data)
            response = await self.llm_manager.generate_response(prompt)
            
            processed_assignment = {
                'title': assignment_data['title'],
                'content': response
            }
            
            logger.info(f"Processed assignment: {processed_assignment['title']}")
            return processed_assignment
        except Exception as e:
            logger.error(f"Failed to process assignment: {str(e)}")
            raise

    def _create_prompt(self, assignment_data):
        return f"""
        Assignment Title: {assignment_data['title']}
        Description: {assignment_data['description']}
        Due Date: {assignment_data['due_date']}
        Points: {assignment_data['points']}

        Please complete this assignment based on the given information. 
        Provide a well-structured response that addresses all aspects of the assignment.
        """
