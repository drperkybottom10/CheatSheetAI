import os
from pydantic import BaseSettings

class Config(BaseSettings):
    CANVAS_URL: str = "https://baps.instructure.com"
    GOOGLE_DOCS_URL: str = "https://docs.google.com"
    
    CANVAS_USERNAME: str
    CANVAS_PASSWORD: str
    GOOGLE_EMAIL: str
    GOOGLE_PASSWORD: str
    
    COURSE_SELECTOR: str
    ASSIGNMENT_SELECTOR: str
    
    OPENAI_API_KEY: str
    
    HEADLESS: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate()

    def validate(self):
        required_vars = [
            "CANVAS_USERNAME", "CANVAS_PASSWORD", "GOOGLE_EMAIL", "GOOGLE_PASSWORD",
            "COURSE_SELECTOR", "ASSIGNMENT_SELECTOR", "OPENAI_API_KEY"
        ]
        for var in required_vars:
            if not getattr(self, var):
                raise ValueError(f"Missing required environment variable: {var}")
