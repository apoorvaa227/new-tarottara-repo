# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
# import time
# import streamlit as st
# from fpdf import FPDF
# from langdetect import detect
# from deep_translator import GoogleTranslator
# from intent.intent import classify_intent_cached
# from tarot.tarot_reader import cached_reading
# from voice.input import record_from_mic, transcribe_audio
# from voice.output import synthesize_voice, play_voice_response
# from fpdf.enums import XPos, YPos


# st.set_page_config(page_title="TarotTara - Your Magical Guide", layout="centered")
# st.title("🔮 TarotTara – Your Magical Tarot Guide")

# # Session state for storing user info
# if "user_info" not in st.session_state:
#     st.session_state.user_info = {}

# if "language" not in st.session_state:
#     st.session_state.language = "en"

# # Function to collect user info
# with st.sidebar:
#     st.header("📋 User Info")
#     with st.form("user_form"):
#         name = st.text_input("Full Name")
#         dob = st.text_input("Date of Birth (DD-MM-YYYY)")
#         birth_place = st.text_input("Place of Birth")
#         birth_time = st.text_input("Time of Birth (e.g. 03:30 PM)")
#         gender = st.selectbox("Gender", ["M", "F", "Other"])
#         mood = st.text_input("How are you feeling today?")
#         day_summary = st.text_input("How is your day going?")
#         language = st.selectbox("Preferred Language", ["en", "hi", "es", "fr"])
#         submit = st.form_submit_button("Save Info")

#     if submit:
#         user_info = {
#             "name": name,
#             "dob": dob,
#             "birth_place": birth_place,
#             "birth_time": birth_time,
#             "gender": gender,
#             "mood": mood,
#             "day_summary": day_summary,
#         }
#         st.session_state.user_info = user_info
#         st.session_state.language = language
#         st.success("User info saved successfully!")

# # Save PDF
#         os.makedirs("user_logs", exist_ok=True)
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Helvetica", size=12)
#         pdf.cell(200, 10, text="TarotTara User Log", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
#         pdf.ln(10)
#         for key, value in user_info.items():
#             pdf.cell(200, 10, text=f"{key.title()}: {value}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
#         filename = f"user_logs/{name.replace(' ', '_')}_log.pdf"
#         pdf.output(filename)

# # Main app input section
# st.subheader("🧘 Ask your question")
# input_method = st.radio("Choose input method", ["Type", "Upload Audio"])

# question = ""
# if input_method == "Type":
#     question = st.text_area("Type your question below:")
# elif input_method == "Upload Audio":
#     audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
#     if audio_file:
#         with st.spinner("Transcribing your audio..."):
#             question = transcribe_audio(audio_file)
#             st.success(f"✅ You said: {question}")

# if st.button("🔮 Submit Question") and question:
#     with st.spinner("Analyzing your question..."):
#         detected_lang = detect(question)
#         translated_question = GoogleTranslator(source='auto', target='en').translate(question) if detected_lang != "en" else question

#         intent_start = time.time()
#         intent = classify_intent_cached(translated_question)
#         intent_duration = time.time() - intent_start

#         prediction_start = time.time()
#         result = cached_reading(translated_question, intent)
#         prediction_duration = time.time() - prediction_start

#         if "error" in result:
#             st.error(f"⚠️ Error: {result['error']}")
#         else:
#             answer_en = result["interpretation"]
#             user_lang = st.session_state.language
#             final_answer = GoogleTranslator(source='en', target=user_lang).translate(answer_en) if user_lang != "en" else answer_en

#             st.markdown("### 🔍 TarotTara says:")
#             if intent == "timeline":
#                 card = result.get("card", "")
#                 date_range = result.get("date_range", ["", ""])
#                 st.write(f"**Card:** {card}")
#                 st.write(f"**Timeframe:** {date_range[0].strftime('%B %d')} – {date_range[1].strftime('%B %d')}")

#             elif intent == "factual":
#                 st.write("**Answer:**")
#             else:
#                 cards = result.get("cards", [])
#                 if cards:
#                     st.write(f"**Cards Drawn:** {', '.join(cards)}")

#             st.success(final_answer)

#             # audio_path = synthesize_voice(final_answer, user_input_lang=user_lang)
#             # if audio_path and os.path.exists(audio_path):
#             #     audio_bytes = open(audio_path, 'rb').read()
#             #     st.audio(audio_bytes, format='audio/mp3')

#             st.markdown(f"⏱️ **Intent classification:** {intent_duration:.2f}s")
#             st.markdown(f"⏱️ **Prediction (LLM + RAG):** {prediction_duration:.2f}s")
import sys
import os
import time
import traceback
import streamlit as st
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
        pdf.cell(200, 10, text="TarotTara User Log", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(10)
        for key, value in st.session_state.user_info.items():
            pdf.cell(200, 10, text=f"{key.title()}: {value}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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

input_method = st.radio("Choose input method", ["Type", "Upload Audio", "Upload Image"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = ""
uploaded_image = None

if input_method == "Type":
    question = st.chat_input("Type your question below:")
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
        question = st.text_input("Ask a question about this image:")

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


