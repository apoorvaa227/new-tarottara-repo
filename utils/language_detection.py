# utils/language_detection.py
import re
from typing import Tuple, Optional
from deep_translator import GoogleTranslator
import logging
import requests
from os import getenv
# import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Universal getter for local + Streamlit Cloud
def get_env(key: str, default=None):
    return os.getenv(key, default)

def groq_invoke(prompt: str, max_tokens: int = 50, temperature: float = 0) -> str:
    """
    Invoke Groq API for language detection.
    Args:
        prompt: The prompt to send to the model
        max_tokens: Maximum tokens for response
        temperature: Temperature for response generation
    Returns:
        The model's response
    """
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = get_env("GROQ_API_KEY")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            logger.error("Groq API rate limit reached")
            return "en"  # Default fallback
        else:
            logger.error(f"Groq API HTTP error: {e}")
            return "en"  # Default fallback
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "en"  # Default fallback

def _detect_by_patterns(text: str) -> Tuple[str, float]:
    """
    Pattern-based language detection for short texts or fallback.
    """
    text = text.lower()
    
    # Hinglish patterns
    hinglish_patterns = ['kaise', 'kya', 'aap', 'mai', 'hoon', 'kar', 'karu', 'accha', 'theek', 'hai', 'nahi']
    if any(pattern in text for pattern in hinglish_patterns):
        return 'hinglish', 0.8

    # Hindi patterns
    if re.search(r'[नमस्तेकैसेहोआपकयाकरूअच्छादिनशुभराम]', text):
        return 'hi', 0.9
    
    # Romanized Hindi patterns
    hindi_rom_patterns = ['namaste', 'kaise', 'kya', 'aap', 'mai', 'hoon', 'kar', 'karu', 'accha', 'theek']
    if any(pattern in text for pattern in hindi_rom_patterns):
        return 'hi_rom', 0.8
    
    # Tamil patterns
    if re.search(r'[வணக்கம்எப்படிஇருக்கிறீர்கள்நான்என்னசெய்வேன்]', text):
        return 'ta', 0.9
    
    # Telugu patterns
    if re.search(r'[నమస్కారంఎలాఉన్నారునేనుఏంచేస్తా]', text):
        return 'te', 0.9
    
    # Bengali patterns
    if re.search(r'[নমস্কারকেমনআছেনআমিকিকরব]', text):
        return 'bn', 0.9
    
    # Spanish patterns
    spanish_patterns = ['hola', 'como', 'estas', 'que', 'tal', 'bien', 'gracias', 'por', 'favor']
    if any(pattern in text for pattern in spanish_patterns):
        return 'es', 0.8
    
    # French patterns
    french_patterns = ['bonjour', 'comment', 'allez', 'vous', 'bien', 'merci', 'oui', 'non', 'tres']
    if any(pattern in text for pattern in french_patterns):
        return 'fr', 0.8
    
    # Default to English
    return 'en', 0.5

def _calculate_confidence(text: str, detected_lang: str) -> float:
    """
    Calculate confidence score based on text characteristics and detected language.
    """
    base_confidence = 0.7
    
    # Increase confidence for longer texts
    if len(text) > 50:
        base_confidence += 0.1
    elif len(text) > 20:
        base_confidence += 0.05
    
    # Language-specific confidence adjustments
    if detected_lang.endswith('_rom'):
        # Romanized languages are harder to detect
        base_confidence -= 0.1
    
    return min(base_confidence, 1.0)

def detect_language_with_groq(text: str) -> Tuple[str, float]:
    """
    Detect language using Groq model with confidence scoring.
    
    Args:
        text: Input text to detect language for
        
    Returns:
        Tuple of (language_code, confidence_score)
    """
    if not text or not text.strip():
        return 'en', 0.0
    
    text = text.strip()
    
    # For very short text, use pattern detection first
    if len(text) < 10:
        pattern_result = _detect_by_patterns(text)
        if pattern_result[1] > 0.7:
            return pattern_result
    
    # Use Groq for language detection
    prompt = f"""You are a language detection expert. Your job is to identify the language of the given text and respond with ONLY the ISO 639-1 language code.

Supported languages and their codes:
- English: en
- Hindi: hi
- Romanized Hindi (Hindi written in English letters): hi_rom
- Marathi: mr
- Romanized Marathi (Marathi written in English letters): mr_rom
- Bengali: bn
- Romanized Bengali (Bengali written in English letters): bn_rom
- Telugu: te
- Romanized Telugu (Telugu written in English letters): te_rom
- Tamil: ta
- Romanized Tamil (Tamil written in English letters): ta_rom
- Gujarati: gu
- Romanized Gujarati (Gujarati written in English letters): gu_rom
- Kannada: kn
- Romanized Kannada (Kannada written in English letters): kn_rom
- Malayalam: ml
- Romanized Malayalam (Malayalam written in English letters): ml_rom
- Punjabi: pa
- Romanized Punjabi (Punjabi written in English letters): pa_rom
- Odia: or
- Romanized Odia (Odia written in English letters): or_rom
- Assamese: as
- Romanized Assamese (Assamese written in English letters): as_rom
- Urdu: ur
- Romanized Urdu (Urdu written in English letters): ur_rom
- Nepali: ne
- Romanized Nepali (Nepali written in English letters): ne_rom
- Spanish: es
- French: fr
- German: de
- Italian: it
- Portuguese: pt
- Vietnamese: vi
- Indonesian: id
- Malay: ms
- Filipino: tl
- Thai: th
- Myanmar: my
- Khmer: km
- Lao: lo
- Sinhala: si

Examples:
Text: "Hello, how are you?"
Language: en

Text: "नमस्ते, कैसे हो आप?"
Language: hi

Text: "mai aj kya kru?"
Language: hi_rom

Text: "mi aaj kay karaycha?"
Language: mr_rom

Text: "ami aj ki korbo?"
Language: bn_rom

Text: "naanu ee em chestha?"
Language: te_rom

Text: "naan inru enna seiven?"
Language: ta_rom

Text: "hu aaj shu karish?"
Language: gu_rom

Text: "Hola, ¿cómo estás?"
Language: es

Text: "Bonjour, comment allez-vous?"
Language: fr

Text: "வணக்கம், எப்படி இருக்கிறீர்கள்?"
Language: ta

Text: "নমস্কার, কেমন আছেন?"
Language: bn

Text: "నమస్కారం, ఎలా ఉన్నారు?"
Language: te

Now detect the language of this text:
Text: "{text}"
Language:"""

    try:
        detected_lang = groq_invoke(prompt, max_tokens=10, temperature=0).strip().lower()
        
        # Validate the detected language
        valid_languages = {
            'en', 'hi', 'hi_rom', 'mr', 'mr_rom', 'bn', 'bn_rom', 'te', 'te_rom', 'ta', 'ta_rom', 
            'gu', 'gu_rom', 'kn', 'kn_rom', 'ml', 'ml_rom', 'pa', 'pa_rom', 'or', 'or_rom', 
            'as', 'as_rom', 'ur', 'ur_rom', 'ne', 'ne_rom',
            'es', 'fr', 'de', 'it', 'pt', 'vi', 'id', 'ms', 'tl', 'th', 'my', 'km', 'lo', 'si'
        }
        
        if detected_lang in valid_languages:
            confidence = _calculate_confidence(text, detected_lang)
            return detected_lang, confidence
        else:
            # Fallback to English for unsupported languages
            return 'en', 0.5
            
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return 'en', 0.5  # Default fallback

def get_language_name(lang_code: str) -> str:
    """
    Get human-readable language name from language code.
    """
    language_names = {
        'en': 'English',
        'hi': 'Hindi',
        'hi_rom': 'Romanized Hindi',
        'mr': 'Marathi',
        'mr_rom': 'Romanized Marathi',
        'bn': 'Bengali',
        'bn_rom': 'Romanized Bengali',
        'te': 'Telugu',
        'te_rom': 'Romanized Telugu',
        'ta': 'Tamil',
        'ta_rom': 'Romanized Tamil',
        'gu': 'Gujarati',
        'gu_rom': 'Romanized Gujarati',
        'kn': 'Kannada',
        'kn_rom': 'Romanized Kannada',
        'ml': 'Malayalam',
        'ml_rom': 'Romanized Malayalam',
        'pa': 'Punjabi',
        'pa_rom': 'Romanized Punjabi',
        'or': 'Odia',
        'or_rom': 'Romanized Odia',
        'as': 'Assamese',
        'as_rom': 'Romanized Assamese',
        'ur': 'Urdu',
        'ur_rom': 'Romanized Urdu',
        'ne': 'Nepali',
        'ne_rom': 'Romanized Nepali',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'ms': 'Malay',
        'tl': 'Filipino',
        'th': 'Thai',
        'my': 'Myanmar',
        'km': 'Khmer',
        'lo': 'Lao',
        'si': 'Sinhala'
    }
    return language_names.get(lang_code, lang_code.upper())

def normalize_language_for_translation(lang_code: str) -> str:
    """
    Convert unsupported language codes to Google Translate compatible codes.
    """
    translation_map = {
        'hinglish': 'hi',  # Treat Hinglish as Hindi for translation purposes
        'hi_rom': 'hi',
        'mr_rom': 'mr',
        'bn_rom': 'bn',
        'te_rom': 'te',
        'ta_rom': 'ta',
        'gu_rom': 'gu',
        'kn_rom': 'kn',
        'ml_rom': 'ml',
        'pa_rom': 'pa',
        'or_rom': 'or',
        'as_rom': 'as',
        'ur_rom': 'ur',
        'ne_rom': 'ne'
    }
    return translation_map.get(lang_code, lang_code)
