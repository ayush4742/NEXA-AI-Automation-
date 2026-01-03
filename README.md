# NEXA — AI Automation & Data Intelligence Studio

NEXA is a desktop AI assistant built with **Python** and **Streamlit** that executes **natural-language voice or text commands** to automate desktop tasks and perform **data cleaning with automatic EDA reports**.

The project combines **rule-based automation** (fast and reliable for common tasks) with **LLM-assisted intelligence** (for flexible and complex commands), making it a practical AI automation studio for daily workflows.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Voice Commands Examples](#voice-commands-examples)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Notes & Safety](#notes--safety)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### 🤖 AI & Desktop Automation
- Open applications (VS Code, browser, WhatsApp, etc.)
- Send WhatsApp messages via voice commands
- Make WhatsApp voice calls
- Control media playback (YouTube / system media)
  - Play / Pause / Resume
  - Mute / Unmute
  - Volume up / down
  - Play songs on YouTube
  - Play next song in a new tab

### 🎙️ Voice Assistant
- Microphone-based voice recognition
- Robust keyword-based command matching
- OS-level media control (reliable across browsers & apps)
- Works independently as a background assistant (`assistant.py`)

### 📊 Data Cleaner & EDA
- Upload CSV or Excel files
- Remove empty rows and duplicate records
- Normalize column names
- Trim text columns
- Generate automatic **EDA report (HTML)**
- Download cleaned dataset and profiling report

### 🧠 Hybrid Intelligence
- Rule-based execution for critical commands (fast & safe)
- LLM fallback (Groq API) for complex or custom automation
- Persistent memory of summarized commands

---

## Tech Stack

- **Python**
- **Streamlit** — UI & dashboard
- **Groq LLM API** — AI code & task generation
- **PyAutoGUI** — Desktop automation
- **SpeechRecognition** — Voice input
- **pandas** — Data processing
- **ydata-profiling** — Automated EDA reports
- **python-dotenv** — Environment variable management

---

## Installation

### 1️⃣ Create & activate virtual environment (recommended)

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash / WSL)