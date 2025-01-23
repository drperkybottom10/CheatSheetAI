import asyncio
import logging
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)

class UIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CheatSheetAI")
        self.root.geometry("400x300")

        self.assignment_label = tk.Label(self.root, text="Assignment Name:")
        self.assignment_label.pack(pady=5)
        self.assignment_entry = tk.Entry(self.root, width=40)
        self.assignment_entry.pack(pady=5)

        self.class_label = tk.Label(self.root, text="Class Name:")
        self.class_label.pack(pady=5)
        self.class_entry = tk.Entry(self.root, width=40)
        self.class_entry.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit_assignment)
        self.submit_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        self.assignment_queue = asyncio.Queue()

    async def start(self):
        logger.info("Starting UI")
        self.root.mainloop()

    def submit_assignment(self):
        assignment_name = self.assignment_entry.get()
        class_name = self.class_entry.get()
        if assignment_name and class_name:
            self.assignment_queue.put_nowait((assignment_name, class_name))
            self.update_status("Assignment submitted. Processing...")
        else:
            self.show_error("Please enter both assignment name and class name.")

    async def get_assignment_input(self):
        return await self.assignment_queue.get()

    def update_status(self, message):
        logger.info(f"Status update: {message}")
        self.status_label.config(text=message)
        self.root.update()

    def show_error(self, error_message):
        logger.error(f"Error: {error_message}")
        messagebox.showerror("Error", error_message)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ui = UIManager()
    ui.run()
