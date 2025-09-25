# listener.py
import speech_recognition as sr
from rich.console import Console

console = Console()

def listen_to_speech(lang="en-IN"):
    """
    Captures speech and converts to text using Google Speech Recognition.
    lang: language code (default: en-IN)
          Examples: 'ta-IN' (Tamil), 'hi-IN' (Hindi), 'te-IN' (Telugu)
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        console.print("[cyan]🎤 Listening... (speak now)[/cyan]")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # better noise handling
        audio = recognizer.listen(source, phrase_time_limit=15)  # max 15s per question

    try:
        text = recognizer.recognize_google(audio, language=lang)
        console.print(f"[green]✅ You said:[/green] {text}")
        return text
    except sr.UnknownValueError:
        console.print("[red]❌ Could not understand audio (try again)[/red]")
        return None
    except sr.RequestError as e:
        console.print(f"[bold red]⚠️ API Error:[/bold red] {e}")
        return None
