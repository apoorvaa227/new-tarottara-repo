# 📁 voice/output.py
import io
import wave
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from pydub import AudioSegment
from playsound import playsound
import tempfile

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("VOICE_ID")
if not api_key or not voice_id:
    raise EnvironmentError("Missing ELEVENLABS_API_KEY or VOICE_ID")

client = ElevenLabs(api_key=api_key)

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
