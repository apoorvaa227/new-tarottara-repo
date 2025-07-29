import sys
import os
import time
import traceback
import uuid
import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from deep_translator import GoogleTranslator
import PyPDF2
from io import BytesIO

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Safe imports with fallbacks
try:
    from utils.language_detection import detect_language_with_groq, get_language_name, normalize_language_for_translation
    LANGUAGE_DETECTION_AVAILABLE = True
except ImportError:
    def detect_language_with_groq(text):
        try:
            from langdetect import detect
            return detect(text), 0.8
        except ImportError:
            return "en", 0.5

    def get_language_name(lang_code):
        names = {'en': 'English', 'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French'}
        return names.get(lang_code, lang_code.upper())

    def normalize_language_for_translation(lang_code):
        return lang_code

    LANGUAGE_DETECTION_AVAILABLE = False

from intent.intent import classify_intent
from tarot.tarot_reader import cached_reading
from ai_request import send_chat_log
from voice.input import transcribe_audio, listen
from utils.llm_chat import generate_conversational_response
from utils.image_processing import process_image_with_question
from voice.output import speak
from utils.session_manager import show_session_loader, save_current_session
from utils.theme_manager import apply_theme, show_theme_toggle, get_title_html

# Debug logger
def debug_log_error(context: str, error: Exception):
    print(f"❌ [{context}] Exception: {error}")
    print(traceback.format_exc())
    if hasattr(error, 'response') and error.response is not None:
        try:
            print("🔎 Response content:", error.response.text)
        except Exception as parse_error:
            print("⚠️ Could not parse error response:", parse_error)

def safe_generate_conversational_response(message: str, user_info: dict = None, detected_lang: str = "en") -> str:
    try:
        return generate_conversational_response(message, user_info, detected_lang)
    except TypeError:
        try:
            return generate_conversational_response(message, user_info)
        except TypeError:
            return generate_conversational_response(message)
    except Exception:
        user_name = user_info.get("name", "friend") if user_info else "friend"
        return f"Hello {user_name}! I'm here to help you with your tarot questions."

st.set_page_config(
    page_title="TarotTara - Your Magical Guide", 
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon="🔮"
)

# Theme is now managed by utils/theme_manager.py

st.markdown(get_title_html(), unsafe_allow_html=True)

# Initialize session state
for key in ["user_info", "language", "messages", "dark_theme"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "user_info" else "en" if key == "language" else [] if key == "messages" else True

# Apply theme
apply_theme(st.session_state.dark_theme)

# Sidebar for user info
with st.sidebar:
    st.header("📋 User Info (Required)")
    user_info_complete = st.session_state.user_info.get("name") and st.session_state.user_info.get("gender")
    if not user_info_complete:
        st.error("⚠️ Please complete your profile to start using TarotTara!")

    with st.form("user_form"):
        name = st.text_input("Full Name *", value=st.session_state.user_info.get("name", ""))
        gender = st.selectbox("Gender *", ["", "M", "F", "Other"], index=["", "M", "F", "Other"].index(st.session_state.user_info.get("gender", "")))
        st.markdown("**Optional Information:**")
        dob = st.text_input("Date of Birth (DD-MM-YYYY)", value=st.session_state.user_info.get("dob", ""))
        birth_place = st.text_input("Place of Birth", value=st.session_state.user_info.get("birth_place", ""))
        birth_time = st.text_input("Time of Birth (e.g. 03:30 PM)", value=st.session_state.user_info.get("birth_time", ""))
        mood = st.text_input("How are you feeling today?", value=st.session_state.user_info.get("mood", ""))
        day_summary = st.text_input("How is your day going?", value=st.session_state.user_info.get("day_summary", ""))
        language = st.selectbox("Preferred Language", ["en", "hi", "es", "fr", "ta", "te", "bn", "gu", "mr", "kn", "ml", "pa", "hinglish"],
                                format_func=lambda x: {"en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
                                                       "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "gu": "Gujarati",
                                                       "mr": "Marathi", "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi",
                                                       "hinglish": "Hinglish"}.get(x, x),
                                index=["en", "hi", "es", "fr", "ta", "te", "bn", "gu", "mr", "kn", "ml", "pa", "hinglish"].index(
                                    st.session_state.user_info.get("language", "en")))
        submit = st.form_submit_button("Save Info")

    if submit and name.strip() and gender:
        st.session_state.user_info = {
            "name": name.strip(),
            "gender": gender,
            "dob": dob or "Not provided",
            "birth_place": birth_place or "Not provided",
            "birth_time": birth_time or "Not provided",
            "mood": mood or "Good",
            "day_summary": day_summary or "Going well",
            "language": language
        }
        st.session_state.language = language
        st.success("User info saved successfully!")
        os.makedirs("user_logs", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, "TarotTara User Log", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        for key, value in st.session_state.user_info.items():
            pdf.cell(200, 10, f"{key.title()}: {value}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        filename = f"user_logs/{name.replace(' ', '_')}_log.pdf"
        pdf.output(filename)

# Session Management in Sidebar
show_session_loader()

# Theme Toggle
show_theme_toggle()

# Save Session Button
if st.sidebar.button("💾 Save Current Session", type="secondary"):
    save_current_session()

# Stop if user info not complete
if not (st.session_state.user_info.get("name") and st.session_state.user_info.get("gender")):
    st.warning("⚠️ Please complete your user profile in the sidebar before asking questions!")
    st.stop()

user_name = st.session_state.user_info["name"]
st.subheader(f"🧘 Hi {user_name}! Ask your question")

# Initialize welcome message
if not st.session_state.messages:
    welcome_msg = f"Hello {user_name}! I'm TarotTara, your personal tarot guide. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Display chat messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Add voice button for assistant messages
        if msg["role"] == "assistant":
            if st.button("🔊 Listen", key=f"listen_{i}"):
                speak(msg["content"])

# Voice input section - Make it more prominent
st.markdown("### 🎤 Voice Input")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🎤 Speak your question", key="mic_input", use_container_width=True, type="primary"):
        with st.spinner("🎤 Listening... Speak now!"):
            try:
                user_voice_input = listen()
                if user_voice_input:
                    st.success(f"✅ You said: {user_voice_input}")
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_voice_input})
                    
                    # Generate bot response for voice input
                    with st.spinner("🔮 TarotTara is analyzing your voice question..."):
                        context = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
                        try:
                            detected_lang, confidence = detect_language_with_groq(user_voice_input)
                            user_lang = st.session_state.language
                            user_name = st.session_state.user_info.get("name", "friend")
                            
                            final_answer = generate_conversational_response(
                                user_voice_input,
                                {"name": user_name, "language": user_lang},
                                detected_lang="hinglish" if user_lang == "hinglish" else detected_lang,
                                context=context
                            )
                            
                            if final_answer and final_answer.strip():
                                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                                st.success("✅ Response generated!")
                                st.rerun()
                            else:
                                st.error("❌ Could not generate response. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error generating response: {str(e)}")
                else:
                    st.error("❌ Could not understand your voice. Please try again.")
            except Exception as e:
                st.error(f"❌ Voice input error: {str(e)}")

with col2:
    if st.button("💾 Save Session", key="save_session_main", use_container_width=True, type="secondary"):
        save_current_session()

# Input method selection
st.markdown("### 📝 Text Input")
input_method = st.radio("Choose input method", ["Type", "Upload Audio", "Upload Image", "Upload PDF"], key="input_method")

question = ""
uploaded_image = None

if input_method == "Type":
    question = st.chat_input("Type your question below:", key="chat_input")
elif input_method == "Upload Audio":
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    if audio_file:
        with st.spinner("Transcribing your audio..."):
            question = transcribe_audio(audio_file)
            st.success(f"✅ You said: {question}")
elif input_method == "Upload Image":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Your uploaded image", use_column_width=True)
        question = st.text_input("Ask a question about this image:", key="image_question")
elif input_method == "Upload PDF":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file:
        with st.spinner("Extracting text from your PDF..."):
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
                pdf_text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text + "\n"
                if not pdf_text.strip():
                    st.error("No text could be extracted from the PDF.")
                else:
                    st.success("✅ Text extracted from PDF!")
                    st.text_area("Extracted Text", pdf_text, height=200)
                    # Ask user for a question based on the document
                    question = st.text_input(
                        "What question do you want to ask based on this document?",
                        placeholder="Type your question here..."
                    )
            except Exception as e:
                st.error(f"Error extracting text from PDF: {e}")

# Handle question processing
if question and (input_method != "Upload Image" or uploaded_image is not None):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display user message
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image, caption="User's image", width=200)
        st.markdown(question)

    # Generate bot response
    with st.spinner("🔮 TarotTara is analyzing your question..."):
        context = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        try:
            # Check if GROQ_API_KEY is available
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                error_msg = "❌ GROQ_API_KEY not found in environment variables. Please check your .env file."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.error(error_msg)
                st.rerun()
            
            detected_lang, confidence = detect_language_with_groq(question)
            user_lang = st.session_state.language
            user_name = st.session_state.user_info.get("name", "friend")
            
            # Debug info
            st.info(f"🔍 Debug: Processing question in {detected_lang} language for user {user_name}")
            
            final_answer = generate_conversational_response(
                question,
                {"name": user_name, "language": user_lang},
                detected_lang="hinglish" if user_lang == "hinglish" else detected_lang,
                context=context
            )
            
            if not final_answer or final_answer.strip() == "":
                error_msg = "Sorry, I couldn't generate a response. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.error(error_msg)
            else:
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(final_answer)
                    
                    # Add voice button for this response
                    if st.button("🔊 Listen to this response", key=f"listen_latest"):
                        speak(final_answer)
                    
        except Exception as e:
            debug_log_error("Chat Response", e)
            error_msg = f"Sorry, I encountered an error while processing your question: {str(e)}. Please check your API keys and try again."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)
    
    # Rerun to update the chat display
    st.rerun()


