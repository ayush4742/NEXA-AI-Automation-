#!/usr/bin/env python
"""
Voice Assistant – Final Stable Version

Features:
- Robust speech recognition (keyword-based)
- OS-level media control (play/pause/mute)
- YouTube control with SAME TAB and NEW TAB logic
- Designed to be started/stopped from J3.py
"""

import time
import webbrowser
import sys
import re

# =========================
# IMPORTS
# =========================
try:
    import speech_recognition as sr
    import pyautogui
    import pywhatkit
    import pygetwindow as gw
except Exception as e:
    print("Missing packages:", e)
    sys.exit(1)

try:
    import pyttsx3
    tts_engine = pyttsx3.init()
except Exception:
    tts_engine = None

# =========================
# GLOBALS
# =========================
r = sr.Recognizer()
last_target = None
last_command_time = 0
COMMAND_COOLDOWN = 1.2  # seconds (prevents echo / double toggle)

# =========================
# SPEAK
# =========================
def say(text: str):
    print("Assistant:", text)
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception:
            pass

# =========================
# WINDOW HELPERS
# =========================
def focus_youtube_window():
    try:
        for title in gw.getAllTitles():
            if title and "youtube" in title.lower():
                gw.getWindowsWithTitle(title)[0].activate()
                return True
    except Exception:
        pass
    return False

def close_youtube():
    try:
        for title in gw.getAllTitles():
            if title and "youtube" in title.lower():
                win = gw.getWindowsWithTitle(title)[0]
                win.activate()
                time.sleep(0.2)
                pyautogui.hotkey("ctrl", "w")  # close tab
                return True
    except Exception:
        pass
    return False

# =========================
# COMMAND HANDLER
# =========================
def handle_command(text: str):
    global last_target, last_command_time

    # Cooldown (prevents TTS echo & rapid repeats)
    now = time.time()
    if now - last_command_time < COMMAND_COOLDOWN:
        return
    last_command_time = now

    t = text.lower().strip()
    print("Parsed:", t)

    # -------------------------
    # OPEN YOUTUBE
    # -------------------------
    if "open youtube" in t:
        say("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        last_target = "youtube"
        return

    # -------------------------
    # CLOSE YOUTUBE
    # -------------------------
    if "close youtube" in t or "exit youtube" in t:
        say("Closing YouTube")
        close_youtube()
        return

    # -------------------------
    # PLAY NEXT SONG (NEW TAB)
    # -------------------------
    if (
        "play next song" in t
        or "open new song" in t
        or "queue" in t
    ):
        song = re.sub(
            r"play next song|open new song|queue|on youtube",
            "",
            t
        ).strip()

        if song:
            say(f"Opening {song} in new tab")
            query = song.replace(" ", "+")
            webbrowser.open_new_tab(
                f"https://www.youtube.com/results?search_query={query}"
            )
            last_target = "youtube"
        return

    # -------------------------
    # PLAY SONG (SAME TAB)
    # -------------------------
    if t.startswith("play ") and ("youtube" in t or last_target == "youtube"):
        song = re.sub(r"play|on youtube|youtube", "", t).strip()
        if song:
            say(f"Playing {song}")
            focus_youtube_window()
            pywhatkit.playonyt(song)
            last_target = "youtube"
        return

    # -------------------------
    # PLAY / PAUSE / RESUME
    # -------------------------
    if "pause" in t or "resume" in t or (t == "play" and last_target == "youtube"):
        say("Toggling play pause")
        pyautogui.press("playpause")   # OS media key
        return

    # -------------------------
    # MUTE
    # -------------------------
    if "mute" in t and "unmute" not in t:
        say("Muting")
        pyautogui.press("volumemute")
        return

    # -------------------------
    # UNMUTE
    # -------------------------
    if "unmute" in t or "sound on" in t:
        say("Unmuting")
        pyautogui.press("volumemute")
        return

    # -------------------------
    # VOLUME UP
    # -------------------------
    if "increase volume" in t or "volume up" in t:
        say("Increasing volume")
        for _ in range(5):
            pyautogui.press("volumeup")
        return

    # -------------------------
    # VOLUME DOWN
    # -------------------------
    if "decrease volume" in t or "volume down" in t:
        say("Decreasing volume")
        for _ in range(5):
            pyautogui.press("volumedown")
        return

    say("Sorry, I didn't understand")

# =========================
# LISTEN LOOP
# =========================
def listen_loop():
    say("Assistant started")

    while True:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = r.listen(source, phrase_time_limit=6)

            text = r.recognize_google(audio, language="en-IN")
            print("Heard:", text)
            handle_command(text)

        except sr.UnknownValueError:
            continue
        except KeyboardInterrupt:
            say("Assistant stopped")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(1)

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    listen_loop()