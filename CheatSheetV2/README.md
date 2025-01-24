# Browser Use Project

This project uses the browser-use package to automate browser interactions using Google's Gemini 1.5 Flash model.

## Setup

1. Ensure you have Python 3.11 or higher installed

2. Create and activate a virtual environment using uv:
```bash
uv venv --python 3.11
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Install Playwright:
```bash
playwright install
```

5. Configure your API key:
   - Copy the provided `.env` file
   - The Google API key is already configured

## Usage

Run the agent with:
```bash
python agent.py
```

The agent will execute the specified task using browser automation and return the results. 