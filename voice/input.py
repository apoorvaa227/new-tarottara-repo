
import speech_recognition as sr
import os
from dotenv import load_dotenv
import assemblyai as aai
from elevenlabs import ElevenLabs
from pydub import AudioSegment
from playsound import playsound
import io
import wave
import tempfile

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("VOICE_ID")
if not api_key or not voice_id:
    raise EnvironmentError("Missing ELEVENLABS_API_KEY or VOICE_ID")

client = ElevenLabs(api_key=api_key)
recognizer = sr.Recognizer()

def convert_mp3_to_wav(mp3_bytes):
    mp3_io = io.BytesIO(mp3_bytes)
    audio = AudioSegment.from_file(mp3_io, format="mp3")
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io

def speak(text):
    audio_stream = client.text_to_speech.convert(voice_id=voice_id, text=text)
    audio_bytes = b''.join(audio_stream)
    
    # Create a temporary file to save the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
    
    try:
        # Play the audio file
        playsound(temp_file_path)
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except:
            pass

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        user_input = recognizer.recognize_google(audio)
        print(f"🧍 You: {user_input}")
        return user_input
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand.")
        return None

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
