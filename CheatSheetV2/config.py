import os
from dotenv import load_dotenv
from pydantic import BaseSettings

class Config(BaseSettings):
    GOOGLE_VERTEXAI_PROJECT: str
    CANVAS_USERNAME: str
    CANVAS_PASSWORD: str
    GOOGLE_EMAIL: str
    GOOGLE_PASSWORD: str
    COURSE_SELECTOR: str
    ASSIGNMENT_SELECTOR: str
    PROVIDED_GOOGLE_DOC_URL: str
    QUIZ_ACCESS_CODE: str = ""

    class Config:
        env_file = '.env'

def load_config():
    load_dotenv()
    return Config()
