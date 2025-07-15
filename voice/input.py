
import speech_recognition as sr
import os
from dotenv import load_dotenv
import assemblyai as aai

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

def record_from_mic():
    """
    Records audio from the microphone and returns recognized text using Google Speech.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Please ask your question.")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")
        return None

def transcribe_audio(audio_file):
    """
    Transcribes uploaded audio file using AssemblyAI.
    """
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text
