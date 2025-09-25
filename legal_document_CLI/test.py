from gtts import gTTS
import playsound

# Tamil text
text = "இது ஒரு சட்ட ஆவண சரிபார்ப்பு"
tts = gTTS(text=text, lang='ta')
tts.save("tamil.mp3")
playsound.playsound("tamil.mp3")
