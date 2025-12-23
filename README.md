# NEXA — AI Automation & Data Intelligence Studio

A desktop AI assistant built with Python and Streamlit that executes natural-language commands to automate desktop tasks and perform data cleaning with automatic EDA reports.

This repository combines lightweight rule-based automation with LLM-assisted code generation to provide practical automation for common workflows (WhatsApp messaging, media playback, app launching, dataset cleaning, and more).

---

**Table of Contents**
- [Features](#features)
- [Tech stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project structure](#project-structure)
- [Environment variables](#environment-variables)
- [Notes & safety](#notes--safety)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- AI-driven desktop automation (send WhatsApp messages, open apps, play YouTube, make desktop calls)
- Voice command input (microphone-based recognition)
- Data cleaner for CSV / Excel: remove empty rows, drop duplicates, normalize/trim columns
- Automatic EDA report generation (HTML) and cleaned dataset export
- Hybrid intelligence: rule-based execution with LLM fallback for complex tasks

## Tech stack

- Python
- Streamlit (UI)
- Groq LLM API (LLM integration)
- PyAutoGUI (desktop automation)
- SpeechRecognition (voice input)
- pandas (data processing)
- ydata-profiling (auto EDA)
- python-dotenv (environment variables)

## Installation

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/Scripts/activate    # On Windows (Git Bash / WSL)
```

2. Install dependencies:

```bash
pip install -r requirements.txt
# or install core deps directly:
pip install streamlit groq pyautogui pandas ydata-profiling python-dotenv SpeechRecognition
```

If you don't have a `requirements.txt`, create one from the dependencies above.

## Usage

1. Create a `.env` file in the project root and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
```

2. Run the Streamlit app:

```bash
streamlit run J3.py
```

3. Example natural-language commands:

- `send hi to aman on whatsapp`
- `play believer on youtube`
- `open vs code`
- `call aman`

Data cleaner commands (via the app UI):

- Upload a CSV/Excel file and choose `Clean` to remove empty rows and duplicates, normalize column names, and trim text fields.
- After cleaning, download the cleaned dataset and the generated `eda_report.html`.

## Project structure

Files in the repository (examples):

- `J3.py` — Main Streamlit application
- `.env` — Environment variables (API keys; not committed)
- `JARVIS_db.txt` — Persistent command memory
- `eda_report.html` — Example auto-generated EDA report
- `cleaned_file.xlsx` — Example cleaned output

Adjust names and locations as needed for your environment.

## Environment variables

- `GROQ_API_KEY` — API key for Groq LLM integration

Keep `.env` out of version control (add it to `.gitignore`).

## Notes & safety

- Desktop automation can control your mouse and keyboard. Use with care and test in a safe environment.
- Do not commit secrets or API keys to a public repository.

## Contributing

Contributions are welcome. Open an issue or submit a pull request with a clear description of your change.

## License

Specify a license for your project (e.g., MIT). If you already have a license file, reference it here.

---

If you'd like, I can also:
- generate a `requirements.txt` based on your current venv
- create a `.gitignore` with `.env` and virtualenv entries
- add a short `usage` section inside the app for command examples

Tell me which of those you'd like next.
