import os
import asyncio
from dotenv import load_dotenv
from agent import main as run_agent

class CheatSheetAICLI:
    def __init__(self):
        load_dotenv()
        self.env_vars = {
            "USERNAME": os.getenv("USERNAME", ""),
            "PASSWORD": os.getenv("PASSWORD", ""),
            "COURSE_SELECTOR": os.getenv("COURSE_SELECTOR", ""),
            "ASSIGNMENT_SELECTOR": os.getenv("ASSIGNMENT_SELECTOR", ""),
            "GOOGLE_EMAIL": os.getenv("GOOGLE_EMAIL", ""),
            "GOOGLE_PASSWORD": os.getenv("GOOGLE_PASSWORD", ""),
            "PROVIDED_GOOGLE_DOC_URL": os.getenv("PROVIDED_GOOGLE_DOC_URL", ""),
        }

    def get_user_input(self, prompt, default):
        return input(f"{prompt} [{default}]: ") or default

    def update_env_vars(self):
        for key, value in self.env_vars.items():
            self.env_vars[key] = self.get_user_input(key, value)
            os.environ[key] = self.env_vars[key]

    def display_menu(self):
        print("\nCheatSheet AI CLI")
        print("1. Update settings")
        print("2. Run CheatSheet AI")
        print("3. Exit")

    async def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-3): ")

            if choice == "1":
                self.update_env_vars()
                print("Settings updated successfully!")
            elif choice == "2":
                print("Running CheatSheet AI...")
                try:
                    await run_agent()
                    print("CheatSheet AI completed successfully!")
                except Exception as e:
                    print(f"Error: {str(e)}")
            elif choice == "3":
                print("Exiting CheatSheet AI. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    cli = CheatSheetAICLI()
    asyncio.run(cli.run())


