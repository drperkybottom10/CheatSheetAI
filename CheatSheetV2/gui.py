import sys
import os
import pathlib

# Add the parent directory of CheatSheetV2 to the Python module search path
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QTabWidget, QProgressBar, QFileDialog, QMessageBox, 
    QComboBox, QCheckBox, QSpinBox, QDateEdit
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSettings
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
import qdarkstyle
import json
from dotenv import load_dotenv
from agent import main as run_agent  # Ensure this refers to the async main function

class AgentThread(QThread):
    output_signal = pyqtSignal(str)

    def run(self):
        import asyncio  # Import within the thread to avoid issues
        try:
            self.output_signal.emit("Starting CheatSheet AI...")
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_agent(self.update_output))
            self.output_signal.emit(str(result))
        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")
        finally:
            loop.close()

    def update_output(self, text):
        self.output_signal.emit(text)

class SettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.settings = QSettings("CheatSheetAI", "GUI")

        self.input_fields = {}
        for key in ["USERNAME", "PASSWORD", "COURSE_SELECTOR", "ASSIGNMENT_SELECTOR", "GOOGLE_EMAIL", "GOOGLE_PASSWORD", "PROVIDED_GOOGLE_DOC_URL"]:
            field_layout = QHBoxLayout()
            label = QLabel(key)
            line_edit = QLineEdit()
            line_edit.setText(self.settings.value(key, ""))
            field_layout.addWidget(label)
            field_layout.addWidget(line_edit)
            self.layout.addLayout(field_layout)
            self.input_fields[key] = line_edit

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

    def save_settings(self):
        for key, field in self.input_fields.items():
            self.settings.setValue(key, field.text())
            os.environ[key] = field.text()
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully!")

class RunTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.run_button = QPushButton("Run CheatSheet AI")
        self.run_button.clicked.connect(parent.run_cheatsheet_ai)
        self.layout.addWidget(self.run_button)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

class AnalyticsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.stats_label = QLabel("Assignment Statistics:")
        self.layout.addWidget(self.stats_label)

        self.completed_assignments = QLabel("Completed Assignments: 0")
        self.layout.addWidget(self.completed_assignments)

        self.average_time = QLabel("Average Completion Time: N/A")
        self.layout.addWidget(self.average_time)

        self.success_rate = QLabel("Success Rate: N/A")
        self.layout.addWidget(self.success_rate)

    def update_stats(self, stats):
        self.completed_assignments.setText(f"Completed Assignments: {stats['completed']}")
        self.average_time.setText(f"Average Completion Time: {stats['avg_time']:.2f} seconds")
        self.success_rate.setText(f"Success Rate: {stats['success_rate']:.2f}%")

class SchedulerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.course_combo = QComboBox()
        self.course_combo.addItems(["Course 1", "Course 2", "Course 3"])  # Populate with actual courses
        self.layout.addWidget(self.course_combo)

        self.assignment_combo = QComboBox()
        self.assignment_combo.addItems(["Assignment 1", "Assignment 2", "Assignment 3"])  # Populate with actual assignments
        self.layout.addWidget(self.assignment_combo)

        self.date_edit = QDateEdit()
        self.layout.addWidget(self.date_edit)

        self.time_spin = QSpinBox()
        self.time_spin.setRange(0, 23)
        self.time_spin.setSuffix(" :00")
        self.layout.addWidget(self.time_spin)

        self.schedule_button = QPushButton("Schedule Assignment")
        self.schedule_button.clicked.connect(self.schedule_assignment)
        self.layout.addWidget(self.schedule_button)

        self.scheduled_assignments = QTextEdit()
        self.scheduled_assignments.setReadOnly(True)
        self.layout.addWidget(self.scheduled_assignments)

    def schedule_assignment(self):
        course = self.course_combo.currentText()
        assignment = self.assignment_combo.currentText()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = f"{self.time_spin.value():02d}:00"
        scheduled = f"{course} - {assignment} scheduled for {date} at {time}\n"
        self.scheduled_assignments.append(scheduled)

class CheatSheetAIGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CheatSheet AI")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('icon.png'))  # Add an icon file to your project

        self.setCentralWidget(QTabWidget())
        self.centralWidget().setTabPosition(QTabWidget.TabPosition.North)
        self.centralWidget().setMovable(True)

        self.settings_tab = SettingsTab(self)
        self.run_tab = RunTab(self)
        self.analytics_tab = AnalyticsTab(self)
        self.scheduler_tab = SchedulerTab(self)

        self.centralWidget().addTab(self.settings_tab, "Settings")
        self.centralWidget().addTab(self.run_tab, "Run")
        self.centralWidget().addTab(self.analytics_tab, "Analytics")
        self.centralWidget().addTab(self.scheduler_tab, "Scheduler")

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        
        export_action = file_menu.addAction("Export Logs")
        export_action.triggered.connect(self.export_logs)
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        self.agent_thread = None
        self.completed_assignments = 0
        self.total_time = 0
        self.successful_assignments = 0

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)

    def run_cheatsheet_ai(self):
        self.run_tab.run_button.setEnabled(False)
        self.run_tab.output_text.clear()
        self.run_tab.progress_bar.setValue(0)

        self.agent_thread = AgentThread()
        self.agent_thread.output_signal.connect(self.update_output)
        self.agent_thread.finished.connect(self.on_agent_finished)
        self.agent_thread.start()

    def update_output(self, text):
        self.run_tab.output_text.append(text)
        self.run_tab.progress_bar.setValue(self.run_tab.progress_bar.value() + 10)
        self.status_bar.showMessage(text)

    def on_agent_finished(self):
        self.run_tab.run_button.setEnabled(True)
        self.run_tab.progress_bar.setValue(100)
        self.status_bar.showMessage("CheatSheet AI process completed")
        
        self.completed_assignments += 1
        self.total_time += 60  # Assuming 60 seconds per assignment for this example
        self.successful_assignments += 1  # Assuming success for this example
        
        stats = {
            "completed": self.completed_assignments,
            "avg_time": self.total_time / self.completed_assignments if self.completed_assignments > 0 else 0,
            "success_rate": (self.successful_assignments / self.completed_assignments * 100) if self.completed_assignments > 0 else 0
        }
        self.analytics_tab.update_stats(stats)

    def export_logs(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Logs", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.run_tab.output_text.toPlainText())
            QMessageBox.information(self, "Logs Exported", f"Logs have been exported to {file_name}")

def create_config_file():
    config = {
        "version": "1.0",
        "name": "CheatSheet AI",
        "description": "An AI-powered tool for automating student assignments",
        "author": "Your Name",
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/yourusername/cheatsheet-ai.git"
        },
        "dependencies": [
            "PyQt6",
            "qdarkstyle",
            "python-dotenv"
        ]
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def check_dependencies():
    try:
        import PyQt6
        import qdarkstyle
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all required dependencies using 'pip install -r requirements.txt'")
        sys.exit(1)

if __name__ == "__main__":
    load_dotenv()
    check_dependencies()
    create_config_file()
    app = QApplication(sys.argv)
    window = CheatSheetAIGUI()
    window.show()
    sys.exit(app.exec())
