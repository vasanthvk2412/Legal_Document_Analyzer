import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("--- Available Voices ---")
for voice in voices:
    print(f"ID: {voice.id}")
    print(f"  Name: {voice.name}")
    print(f"  Lang: {voice.languages}")
    print("-" * 20)