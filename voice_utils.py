import os
from dotenv import load_dotenv
import assemblyai as aai
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound

load_dotenv()

# Load AssemblyAI API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


def transcribe_audio(audio_file):
    """
    Transcribes uploaded audio file using AssemblyAI.
    """
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text


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


def synthesize_voice(text, user_input_lang='en', filename="response_audio.mp3"):
    """
    Converts already translated (or original) text to speech using gTTS.
    """
    try:
        # Remove old audio file if exists
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                print(f"⚠️ Could not delete existing audio file: {e}")
                return None

        # Use gTTS with proper language
        tts = gTTS(text=text, lang=user_input_lang)
        tts.save(filename)
        return filename

    except Exception as e:
        print("⚠️ Error generating voice:")
        print(e)
        return None
