import logging
import google.generativeai as genai
import os
import requests
from datetime import datetime, timedelta
from dateutil import parser
import nltk
import json

logger = logging.getLogger(__name__)

def download_nltk_data():
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Call the download function during initialization
download_nltk_data()

async def generate_assignment_response(prompt: str):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.7
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Failed to generate assignment response using Gemini: {e}")
        return f"Failed to generate assignment response using Gemini: {str(e)}"

async def check_plagiarism(text: str):
    try:
        api_key = os.getenv("PLAGIARISM_API_KEY")
        url = "https://api.plagiarismchecker.com/check"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"text": text}
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result["plagiarism_score"] > 20:
            return f"Warning: Potential plagiarism detected. Score: {result['plagiarism_score']}%"
        else:
            return "Plagiarism check completed. No significant issues found."
    except Exception as e:
        logger.error(f"Failed to check plagiarism: {str(e)}")
        return f"Failed to check plagiarism: {str(e)}"

async def set_reminders(assignment_details: dict):
    try:
        due_date = parser.parse(assignment_details['due_date'])
        reminder_date = due_date - timedelta(days=1)
        
        # Ensure calendar API integration is robust
        calendar_api.create_event(
            title=f"Reminder: {assignment_details['title']} due tomorrow",
            date=reminder_date
        )
        return f"Reminder set for {reminder_date} for assignment: {assignment_details['title']}"
    except Exception as e:
        logger.error(f"Failed to set reminder: {e}")
        return f"Failed to set reminder: {str(e)}"

def analyze_assignment_description(description: str):
    try:
        keywords = extract_keywords(description)
        requirements = extract_requirements(description)
        due_date = extract_due_date(description)
        
        return {
            "keywords": keywords,
            "requirements": requirements,
            "due_date": due_date
        }
    except Exception as e:
        logger.error(f"Failed to analyze assignment description: {e}")
        return f"Failed to analyze assignment description: {str(e)}"

def extract_keywords(text: str):
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        
        stop_words = set(nltk.corpus.stopwords.words('english'))
        word_tokens = nltk.tokenize.word_tokenize(text.lower())
        
        keywords = [word for word in word_tokens if word.isalnum() and word not in stop_words]
        return list(set(keywords))[:10]
    except Exception as e:
        logger.error(f"Failed to extract keywords: {str(e)}")
        return []

def extract_requirements(text: str):
    try:
        import re
        
        requirement_patterns = r"(must|should|need to|required to|expected to).*?[.!?]"
        requirements = re.findall(requirement_patterns, text, re.IGNORECASE)
        return [req.strip() for req in requirements]
    except Exception as e:
        logger.error(f"Failed to extract requirements: {str(e)}")
        return []

def extract_due_date(text: str):
    try:
        return str(parser.parse(text, fuzzy=True).date())
    except Exception as e:
        logger.error(f"Failed to extract due date: {str(e)}")
        return None

def store_learning_data(action_name: str, features: list, label: int):
    try:
        with open('learning_data.json', 'a') as f:
            json.dump({'action': action_name, 'features': features, 'label': label}, f)
            f.write('\n')
    except Exception as e:
        logger.error(f"Failed to store learning data: {str(e)}")

def retrieve_learning_data():
    try:
        with open('learning_data.json', 'r') as f:
            return [json.loads(line) for line in f]
    except FileNotFoundError:
        return []
    except Exception as e:
        logger.error(f"Failed to retrieve learning data: {str(e)}")
        return []
