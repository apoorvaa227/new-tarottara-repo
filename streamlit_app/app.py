import sys
import os
import time
import traceback
import uuid  # Import uuid module
# import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from deep_translator import GoogleTranslator

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
from voice.input import transcribe_audio
from utils.llm_chat import generate_conversational_response
from utils.image_processing import process_image_with_question

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

st.set_page_config(page_title="TarotTara - Your Magical Guide", layout="centered")
st.title("🔮 TarotTara – Your Magical Tarot Guide")

# Initialize session state
for key in ["user_info", "language", "messages"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "user_info" else "en" if key == "language" else []

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

# Stop if user info not complete
if not (st.session_state.user_info.get("name") and st.session_state.user_info.get("gender")):
    st.warning("⚠️ Please complete your user profile in the sidebar before asking questions!")
    st.stop()

user_name = st.session_state.user_info["name"]
st.subheader(f"🧘 Hi {user_name}! Ask your question")

if not st.session_state.messages:
    welcome_msg = f"Hello {user_name}! I'm TarotTara, your personal tarot guide. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

input_method = st.radio("Choose input method", ["Type", "Upload Audio", "Upload Image"], key="unique_input_method_radio_1")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = ""
uploaded_image = None

if input_method == "Type":
    question = st.chat_input("Type your question below:", key="unique_chat_input_1")
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
        question = st.text_input("Ask a question about this image:", key="unique_text_input_1")

# Handle question with context memory
if question and (input_method != "Upload Image" or uploaded_image is not None):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image, caption="User's image", width=200)
        st.markdown(question)

    with st.spinner("Analyzing your question..."):
        context = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        try:
            detected_lang, confidence = detect_language_with_groq(question)
            user_lang = st.session_state.language
            user_name = st.session_state.user_info.get("name", "friend")  # Extract user's name
            final_answer = generate_conversational_response(
                question,
                {"name": user_name, "language": user_lang},  # Pass only relevant fields
                detected_lang="hinglish" if user_lang == "hinglish" else detected_lang,
                context=context
            )
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            with st.chat_message("assistant"):
                st.markdown(final_answer)
        except Exception as e:
            debug_log_error("Chat Response", e)
            st.error(f"Error generating response: {e}")
# if audio_file:
#     with st.spinner("Transcribing your audio..."):
#         question = transcribe_audio(audio_file)
#         st.success(f"✅ You said: {question}")
elif input_method == "Upload Image":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        st.image(uploaded_image, caption="Your uploaded image", use_column_width=True)
        question = st.text_input("Ask a question about this image:", key="unique_text_input_2")

# Handle question with context memory
if question and (input_method != "Upload Image" or uploaded_image is not None):
    # Generate a unique session ID for the current session
    session_id = st.session_state.get("session_id", str(uuid.uuid4()))  # Use uuid module
    st.session_state["session_id"] = session_id

    # Save the current message
    st.session_state.messages.append({"role": "user", "content": question})
    # save_chat_history(session_id, st.session_state.messages)

    # ...existing code...
    try:
        detected_lang, confidence = detect_language_with_groq(question)
        user_lang = st.session_state.language
        user_name = st.session_state.user_info.get("name", "friend")  # Extract user's name
        final_answer = generate_conversational_response(
            question,
            {"name": user_name, "language": user_lang},  # Pass only relevant fields
            detected_lang="hinglish" if user_lang == "hinglish" else detected_lang,
            context=context
        )
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        # save_chat_history(session_id, st.session_state.messages)
        with st.chat_message("assistant"):
            st.markdown(final_answer)
    except Exception as e:
        debug_log_error("Chat Response", e)
        st.error(f"Error generating response: {e}")
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

# Stop if user info not complete
if not (st.session_state.user_info.get("name") and st.session_state.user_info.get("gender")):
    st.warning("⚠️ Please complete your user profile in the sidebar before asking questions!")
    st.stop()

user_name = st.session_state.user_info["name"]
st.subheader(f"🧘 Hi {user_name}! Ask your question")

if not st.session_state.messages:
    welcome_msg = f"Hello {user_name}! I'm TarotTara, your personal tarot guide. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

input_method = st.radio("Choose input method", ["Type", "Upload Audio", "Upload Image"], key="unique_input_method_radio_2")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = ""
uploaded_image = None

if input_method == "Type":
    question = st.chat_input("Type your question below:", key="unique_chat_input_2")
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
        question = st.text_input("Ask a question about this image:", key="unique_text_input_3")

# Handle question with context memory
if question and (input_method != "Upload Image" or uploaded_image is not None):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image, caption="User's image", width=200)
        st.markdown(question)

    with st.spinner("Analyzing your question..."):
        context = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        try:
            detected_lang, confidence = detect_language_with_groq(question)
            user_lang = st.session_state.language
            user_name = st.session_state.user_info.get("name", "friend")  # Extract user's name
            final_answer = generate_conversational_response(
                question,
                {"name": user_name, "language": user_lang},  # Pass only relevant fields
                detected_lang="hinglish" if user_lang == "hinglish" else detected_lang,
                context=context
            )
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            with st.chat_message("assistant"):
                st.markdown(final_answer)
        except Exception as e:
            debug_log_error("Chat Response", e)
            st.error(f"Error generating response: {e}")


