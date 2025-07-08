
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
#         pdf.cell(200, 10, txt="TarotTara User Log", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
#         pdf.ln(10)
#         for key, value in user_info.items():
#             pdf.cell(200, 10, txt=f"{key.title()}: {value}", ln=True)
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
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import time
import streamlit as st
from fpdf import FPDF
from utils.language_detection import detect_language_with_groq, get_language_name, normalize_language_for_translation
from deep_translator import GoogleTranslator
from intent.intent import classify_intent
from tarot.tarot_reader import cached_reading
from ai_request import send_chat_log
from voice.input import record_from_mic, transcribe_audio
from voice.output import synthesize_voice, play_voice_response
from fpdf.enums import XPos, YPos
from utils.llm_chat import generate_conversational_response
# from dotenv import load_dotenv
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")


st.set_page_config(page_title="TarotTara - Your Magical Guide", layout="centered")
st.title("🔮 TarotTara – Your Magical Tarot Guide")

# Session state
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "language" not in st.session_state:
    st.session_state.language = "en"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: User Info Form (Mandatory)
with st.sidebar:
    st.header("📋 User Info (Required)")
    
    # Check if user info is complete
    user_info_complete = (
        st.session_state.user_info.get("name") and 
        st.session_state.user_info.get("gender")
    )
    
    if not user_info_complete:
        st.error("⚠️ Please complete your profile to start using TarotTara!")
    
    with st.form("user_form"):
        name = st.text_input("Full Name *", value=st.session_state.user_info.get("name", ""))
        gender = st.selectbox("Gender *", ["", "M", "F", "Other"], 
                             index=["", "M", "F", "Other"].index(st.session_state.user_info.get("gender", "")))
        
        st.markdown("**Optional Information:**")
        dob = st.text_input("Date of Birth (DD-MM-YYYY)", value=st.session_state.user_info.get("dob", ""))
        birth_place = st.text_input("Place of Birth", value=st.session_state.user_info.get("birth_place", ""))
        birth_time = st.text_input("Time of Birth (e.g. 03:30 PM)", value=st.session_state.user_info.get("birth_time", ""))
        mood = st.text_input("How are you feeling today?", value=st.session_state.user_info.get("mood", ""))
        day_summary = st.text_input("How is your day going?", value=st.session_state.user_info.get("day_summary", ""))
        language = st.selectbox("Preferred Language", 
                               ["en", "hi", "es", "fr", "ta", "te", "bn", "gu", "mr", "kn", "ml", "pa"],
                               format_func=lambda x: {
                                   "en": "English", "hi": "Hindi", "es": "Spanish", "fr": "French",
                                   "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "gu": "Gujarati",
                                   "mr": "Marathi", "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi"
                               }.get(x, x),
                               index=["en", "hi", "es", "fr", "ta", "te", "bn", "gu", "mr", "kn", "ml", "pa"].index(st.session_state.user_info.get("language", "en")))
        submit = st.form_submit_button("Save Info")

    if submit:
        if name.strip() and gender:
            user_info = {
                "name": name.strip(),
                "gender": gender,
                "dob": dob or "Not provided",
                "birth_place": birth_place or "Not provided",
                "birth_time": birth_time or "Not provided",
                "mood": mood or "Good",
                "day_summary": day_summary or "Going well",
                "language": language
            }
            st.session_state.user_info = user_info
        st.session_state.language = language
        st.success("User info saved successfully!")

        os.makedirs("user_logs", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(200, 10, txt="TarotTara User Log", ln=True, align="C")
        pdf.ln(10)
        for key, value in user_info.items():
            pdf.cell(200, 10, txt=f"{key.title()}: {value}", ln=True)
        filename = f"user_logs/{name.replace(' ', '_')}_log.pdf"
        pdf.output(filename)

# Chat Interface
user_info_complete = (
    st.session_state.user_info.get("name") and 
    st.session_state.user_info.get("gender")
)

if not user_info_complete:
    st.warning("⚠️ Please complete your user profile in the sidebar before asking questions!")
    st.stop()

user_name = st.session_state.user_info.get("name", "friend")
st.subheader(f"🧘 Hi {user_name}! Ask your question")

# Welcome message for new users
if not st.session_state.messages:
    welcome_msg = f"Hello {user_name}! I'm TarotTara, your personal tarot guide. How can I help you today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

input_method = st.radio("Choose input method", ["Type", "Upload Audio"])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = ""
if input_method == "Type":
    question = st.chat_input("Type your question below:")
elif input_method == "Upload Audio":
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    if audio_file:
        with st.spinner("Transcribing your audio..."):
            question = transcribe_audio(audio_file)
            st.success(f"✅ You said: {question}")

# Handle question
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("Analyzing your question..."):
        # Advanced language detection using Groq
        detected_lang, confidence = detect_language_with_groq(question)
        
        # Show language detection info in sidebar or as expandable info
        with st.expander("🌍 Language Detection"):
            st.write(f"**Detected Language:** {get_language_name(detected_lang)}")
            st.write(f"**Confidence:** {confidence:.2f}")
            if detected_lang.endswith('_rom'):
                st.info(f"📝 Detected romanized text in {get_language_name(detected_lang.replace('_rom', ''))} language")
        
        # Normalize language for translation
        translation_lang = normalize_language_for_translation(detected_lang)
        translated_question = GoogleTranslator(source=translation_lang, target='en').translate(question) if translation_lang != "en" else question

        intent_start = time.time()
        intent = classify_intent(translated_question)
        intent_duration = time.time() - intent_start

        if intent == "conversation":
            final_answer = generate_conversational_response(translated_question, st.session_state.user_info, detected_lang)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            with st.chat_message("assistant"):
              st.markdown(final_answer)
              st.markdown(f"⏱️ **Intent classification:** {intent_duration:.2f}s")
        else:
            prediction_start = time.time()
            user_name = st.session_state.user_info.get("name", "")
            user_gender = st.session_state.user_info.get("gender", "")
            result = cached_reading(translated_question, intent, user_name, user_gender, detected_lang)
            prediction_duration = time.time() - prediction_start

            if "error" in result:
                st.error(f"⚠️ Error: {result['error']}")
            else:
                answer_en = result["interpretation"]
                user_lang = st.session_state.language
                final_answer = GoogleTranslator(source='en', target=user_lang).translate(answer_en) if user_lang != "en" else answer_en
                send_chat_log(question=translated_question, answer=answer_en, intent_type=intent, duration=prediction_duration)

                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                with st.chat_message("assistant"):
                    st.markdown(f"### 🔍 TarotTara's reading for {user_name}:")

                    if intent == "timeline":
                        card = result.get("card", "")
                        date_range = result.get("date_range", ["", ""])
                        st.write(f"**Card:** {card}")
                        st.write(f"**Timeframe:** {date_range[0].strftime('%B %d')} – {date_range[1].strftime('%B %d')}")

                    elif intent == "factual":
                        st.write(f"**Answer for {user_name}:**")
                    else:
                        cards = result.get("cards", [])
                        if cards:
                            st.write(f"**Cards Drawn for {user_name}:** {', '.join(cards)}")

                    st.success(final_answer)
                    st.markdown(f"⏱️ **Intent classification:** {intent_duration:.2f}s")
                    st.markdown(f"⏱️ **Prediction (LLM + RAG):** {prediction_duration:.2f}s")
