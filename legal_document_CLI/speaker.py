# speaker.py

import pyttsx3
from rich.console import Console
from gtts import gTTS
import pygame
import os

console = Console()

# --- LANGUAGE MAP ---
LANGUAGE_CODES = {
    # --- Indian languages ---
    "english": "en",
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "malayalam": "ml",
    "kannada": "kn",
    "marathi": "mr",
    "gujarati": "gu",
    "bengali": "bn",
    "punjabi": "pa",
    "urdu": "ur",
    "odia": "or",
    "assamese": "as",
    "sanskrit": "sa",

    # --- Some world languages ---
    "french": "fr",
    "german": "de",
    "spanish": "es",
    "italian": "it",
    "russian": "ru",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh-cn",
    "arabic": "ar",
    "portuguese": "pt",
}

def normalize_lang(lang: str) -> str:
    """Normalize user input into gTTS language code."""
    if not lang:
        return "en"
    lang = lang.lower().strip()
    return LANGUAGE_CODES.get(lang, lang[:2])  # fallback: first 2 letters


def speak_text(text, lang="en"):
    """
    Speaks text aloud.
    - English (offline) → pyttsx3
    - Other languages → gTTS + pygame
    """
    try:
        lang_code = normalize_lang(lang)

        if lang_code == "en":
            # Offline English TTS
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        else:
            # gTTS for regional & world languages
            filename = "tts_output.mp3"
            tts = gTTS(text=text, lang=lang_code)
            tts.save(filename)

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue

            pygame.mixer.quit()
            os.remove(filename)

    except Exception as e:
        console.print(f"[bold red]Text-to-Speech Error:[/bold red] {e}")
