# =========================
# IMPORTS
# =========================
import re
import sys
import subprocess
import importlib
import streamlit as st
import speech_recognition as sr
import pandas as pd
from groq import Groq
from ydata_profiling import ProfileReport
from dotenv import load_dotenv
import os
from PIL import ImageGrab
load_dotenv()


# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(page_title="NEXA", layout="wide")

if "mode" not in st.session_state:
    st.session_state.mode = None

# =========================
# GROQ CLIENT
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ API key not found. Check your .env file.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =========================
# LOAD FILES
# =========================
try:
    with open("Refrence Codes for Jarvis.txt", "r", encoding="utf-8") as f:
        data = f.read()
except FileNotFoundError:
    data = ""

try:
    with open("JARVIS_db.txt", "r", encoding="utf-8") as f:
        db = f.read()
except FileNotFoundError:
    db = ""

# =========================
# PROMPTS
# =========================
prompt = """
You are JarvisCoder v2 — an autonomous coding & automation engine.
Task: {topic}
Reference Codes: {codes}
Database Context: {database}
Return ONLY executable Python code.
"""

prompt_db = """
Summarize the following user request in 3–4 concise sentences:
{topic}
"""

# =========================
# LLM FUNCTIONS
# =========================
def get_code(topic: str, database: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{
            "role": "system",
            "content": prompt.format(
                topic=topic,
                database=database,
                codes=data
            )
        }]
    )
    return response.choices[0].message.content


def get_db(topic: str) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{
            "role": "system",
            "content": prompt_db.format(topic=topic)
        }]
    )
    return response.choices[0].message.content


# =========================
# SANITIZE LLM OUTPUT
# =========================
def sanitize_code(code: str) -> str:
    """Clean LLM output before exec:
    - If code is wrapped in triple-backtick fences (``` or ```python), extract inner block.
    - Remove stray fence lines if present.
    - Strip leading/trailing whitespace.
    """
    if not isinstance(code, str):
        return ""

    # Look for a fenced code block and extract the first one
    m = re.search(r"```(?:python|py)?\n([\s\S]*?)\n```", code, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Remove any remaining triple-backtick lines
    lines = [ln for ln in code.splitlines() if not ln.strip().startswith("```")]
    cleaned = "\n".join(lines).strip()

    # Sometimes LLMs include markdown code fences with language on the same line
    cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    return cleaned.strip()

# =========================
# DATA CLEANER
# =========================
def clean_excel_or_csv(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df = df.dropna(how="all")
    df = df.drop_duplicates()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

# =========================
# AUTO PACKAGE IMPORT
# =========================
def auto_import_packages(code: str):
    imports = re.findall(r"^\s*import (\w+)|^\s*from (\w+)", code, re.MULTILINE)
    packages = {i[0] or i[1] for i in imports if i[0] or i[1]}

    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# =========================
# VOICE INPUT
# =========================
r = sr.Recognizer()

def listen():
    st.info("🎙️ Listening...")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source)
        text = r.recognize_google(audio, language="en-IN")
        st.success(f"You said: {text}")
        return text
    except Exception:
        st.error("Could not understand audio")
        return None
    
    
    
    
def rule_based_executor(user_text: str) -> bool:
    text = user_text.lower()

    # 🎵 YouTube
    if "play" in text and "youtube" in text:
        import pywhatkit as kit
        song = text.replace("play", "").replace("on youtube", "").strip()
        kit.playonyt(song)
        return True

    # 📂 Open App / File
    if "open" in text:
        import pyautogui, time
        app = text.replace("open", "").strip()
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.typewrite(app)
        time.sleep(1)
        pyautogui.press('enter')
        return True

    # 💬 WhatsApp Message
    if "send" in text and "whatsapp" in text:
        import pyautogui, time
        parts = text.replace("send", "").replace("on whatsapp", "").split("to")
        message = parts[0].strip()
        contact = parts[1].strip()

        pyautogui.press('win')
        pyautogui.typewrite('whatsapp')
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'f')
        pyautogui.typewrite(contact)
        time.sleep(1)
        pyautogui.press('enter')
        pyautogui.typewrite(message)
        pyautogui.press('enter')
        return True

    # 📞 WhatsApp Call
    if "call" in text and "whatsapp" in text:
        import pyautogui, time
        contact = text.replace("call", "").replace("on whatsapp", "").strip()

        pyautogui.press('win')
        pyautogui.typewrite('whatsapp')
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'f')
        pyautogui.typewrite(contact)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.click(1747, 82)  # voice call
        return True

    return False

# =========================
# CORE COMMAND PROCESSOR
# =========================
def process_command(user_text: str):
    global db
    lower = user_text.lower()

    # -----------------------------
    # 1️⃣ MODE SWITCH (DATA CLEANER)
    # -----------------------------
    if "clean" in lower and ("csv" in lower or "excel" in lower or "database" in lower):
        st.session_state.mode = "clean"
        return

    # ------------------------------------
    # 2️⃣ RULE-BASED AUTOMATION (CRITICAL)
    # ------------------------------------
    # If command is handled here, STOP.
    if rule_based_executor(user_text):
        return

    # ------------------------------------
    # 3️⃣ FALLBACK TO AI (ONLY IF NEEDED)
    # ------------------------------------
    with st.spinner("Processing with NEXA..."):
        code = get_code(user_text, db)

    # Sanitize LLM output (strip markdown fences or backticks)
    code = sanitize_code(code)

    # Save memory
    db_content = get_db(lower)
    with open("JARVIS_db.txt", "a", encoding="utf-8") as f:
        f.write(db_content + "\n")
        db += "\n" + db_content

    # Show generated code
    st.subheader("Generated Automation Code")
    st.code(code, language="python")

    # Auto-install imports & execute
    auto_import_packages(code)
    exec(code, globals())

# =========================
# HERO SECTION
# =========================
st.markdown("""
<style>
.nexa-hero {
    min-height: 55vh;
    display:flex;
    align-items:center;
    justify-content:center;
    background: radial-gradient(circle,#ff5ccd,#1a0b2e);
}
.nexa-title {
    font-size:4rem;
    font-weight:800;
    color:white;
    letter-spacing:0.2em;
}
</style>
<div class="nexa-hero">
  <div class="nexa-title">NEXA</div>
</div>
""", unsafe_allow_html=True)

# =========================
# MODE SELECTOR
# =========================
st.markdown("### 🚀 Select Operation Mode")

mode = st.radio(
    "",
    ["AI Automation", "Data Cleaner"],
    horizontal=True
)

st.session_state.mode = None if mode == "AI Automation" else "clean"

# =========================
# DATA CLEANER UI
# =========================
if st.session_state.mode == "clean":
    st.subheader("🧹 Database Cleaner")

    uploaded_file = st.file_uploader("Upload CSV or Excel", ["csv", "xlsx"])

    if uploaded_file:
        original_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        uploaded_file.seek(0)

        rows_before = len(original_df)
        empty_rows = original_df.isna().all(axis=1).sum()
        duplicate_rows = original_df.duplicated().sum()

        if st.button("🧼 Clean File"):
            cleaned_df = clean_excel_or_csv(uploaded_file)
            rows_after = len(cleaned_df)

            st.success("File cleaned successfully!")

            st.subheader("📊 Cleaning Statistics")
            st.write(f"Rows before: {rows_before}")
            st.write(f"Rows after: {rows_after}")
            st.write(f"Empty rows removed: {empty_rows}")
            st.write(f"Duplicate rows removed: {duplicate_rows}")

            report = ProfileReport(cleaned_df, explorative=True)
            report_path = "eda_report.html"
            report.to_file(report_path)

            cleaned_df.to_excel("cleaned_file.xlsx", index=False)

            st.download_button("⬇️ Download Cleaned File", open("cleaned_file.xlsx", "rb"), "cleaned_file.xlsx")
            st.download_button("⬇️ Download EDA Report", open(report_path, "rb"), "eda_report.html")

    st.button("🔙 Exit Cleaner", on_click=lambda: st.session_state.update({"mode": None}))

# =========================
# AI AUTOMATION UI
# =========================
if st.session_state.mode is None:
    st.subheader("🤖 AI Automation Console")

    typed_command = st.text_input("Enter command", placeholder="send hi to aman on whatsapp")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎙️ Speak"):
            cmd = listen()
            if cmd:
                process_command(cmd)

    with col2:
        if st.button("⚡ Run"):
            if typed_command.strip():
                process_command(typed_command.strip())
            else:
                st.warning("Please enter a command")
    # Assistant control buttons
    col3 = st.columns(1)[0]
    with col3:
        if st.button("🟢 Start Assistant"):
            proc = st.session_state.get("assistant_proc")
            if proc is None:
                try:
                    p = subprocess.Popen([sys.executable, "assistant.py"])
                    st.session_state["assistant_proc"] = p
                    st.success("Assistant started")
                except Exception as e:
                    st.error(f"Failed to start assistant: {e}")
            else:
                st.info("Assistant already running")

        if st.button("🔴 Stop Assistant"):
            proc = st.session_state.get("assistant_proc")
            if proc:
                try:
                    proc.terminate()
                    st.session_state["assistant_proc"] = None
                    st.success("Assistant stopped")
                except Exception as e:
                    st.error(f"Failed to stop assistant: {e}")
            else:
                st.info("Assistant not running")

    # Skip Ad button capture tool
    st.markdown("---")
    st.subheader("📸 Template Capture for Ad Skip")
    st.write("When a YouTube ad appears, use this to capture the 'Skip Ad' button so voice control can click it automatically.")
    
    col_x1, col_x2, col_x3, col_x4 = st.columns(4)
    with col_x1:
        x1 = st.number_input("Top-left X", value=1700, step=10)
    with col_x2:
        y1 = st.number_input("Top-left Y", value=10, step=10)
    with col_x3:
        x2 = st.number_input("Bottom-right X", value=1920, step=10)
    with col_x4:
        y2 = st.number_input("Bottom-right Y", value=60, step=10)
    
    if st.button("📷 Capture Skip Ad Button"):
        try:
            # Capture the region
            region = (int(x1), int(y1), int(x2), int(y2))
            img = ImageGrab.grab(bbox=region)
            img.save("skip_ad.png")
            st.success(f"✅ Saved skip_ad.png! Region: {region}")
            st.image(img, caption="Captured Skip Ad Button", use_container_width=True)
        except Exception as e:
            st.error(f"Failed to capture: {e}")

    # Auto-detect using OpenCV template match (uses saved skip_ad.png as template)
    try:
        import cv2
        import numpy as np
        has_cv = True
    except Exception:
        cv2 = None
        np = None
        has_cv = False

    if st.button("🧭 Auto-detect Skip Now"):
        if not os.path.exists('skip_ad.png'):
            st.error('No skip_ad.png found — capture it first')
        elif not has_cv:
            st.error('OpenCV not installed. Run: pip install opencv-python numpy')
        else:
            try:
                import pyautogui
                # take full screenshot
                s = pyautogui.screenshot()
                screen = cv2.cvtColor(np.array(s), cv2.COLOR_RGB2BGR)
                tpl = cv2.imread('skip_ad.png', cv2.IMREAD_COLOR)
                th, tw = tpl.shape[:2]
                best_val = -1
                best_loc = None
                best_scale = 1.0
                for scale in np.linspace(0.8, 1.2, 9):
                    try:
                        resized = cv2.resize(tpl, (int(tw*scale), int(th*scale)), interpolation=cv2.INTER_AREA)
                    except Exception:
                        continue
                    if resized.shape[0] < 5 or resized.shape[1] < 5:
                        continue
                    res = cv2.matchTemplate(screen, resized, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(res)
                    if max_val > best_val:
                        best_val = max_val
                        best_loc = max_loc
                        best_scale = scale
                if best_val >= 0.55 and best_loc is not None:
                    x, y = best_loc
                    h, w = int(th*best_scale), int(tw*best_scale)
                    cv2.rectangle(screen, (x,y), (x+w, y+h), (0,255,0), 3)
                    out = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
                    from PIL import Image
                    im = Image.fromarray(out)
                    im.save('skip_ad_found.png')
                    st.image(im, caption=f'Auto-detect found match (score {best_val:.2f})', use_column_width=True)
                    st.success(f'Found match at {x,y} score {best_val:.2f}. Saved skip_ad_found.png')
                else:
                    st.warning('No confident match found (try recapturing template or adjust capture region)')
            except Exception as e:
                st.error(f'Auto-detect failed: {e}')