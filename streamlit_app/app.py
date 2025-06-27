
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import time
import streamlit as st
from fpdf import FPDF
from langdetect import detect
from deep_translator import GoogleTranslator
from intent.intent import classify_intent_cached
from tarot.tarot_reader import cached_reading
from voice.input import record_from_mic, transcribe_audio
from voice.output import synthesize_voice, play_voice_response

st.set_page_config(page_title="TarotTara - Your Magical Guide", layout="centered")
st.title("🔮 TarotTara – Your Magical Tarot Guide")

# Session state for storing user info
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

if "language" not in st.session_state:
    st.session_state.language = "en"

# Function to collect user info
with st.sidebar:
    st.header("📋 User Info")
    with st.form("user_form"):
        name = st.text_input("Full Name")
        dob = st.text_input("Date of Birth (DD-MM-YYYY)")
        birth_place = st.text_input("Place of Birth")
        birth_time = st.text_input("Time of Birth (e.g. 03:30 PM)")
        gender = st.selectbox("Gender", ["M", "F", "Other"])
        mood = st.text_input("How are you feeling today?")
        day_summary = st.text_input("How is your day going?")
        language = st.selectbox("Preferred Language", ["en", "hi", "es", "fr"])
        submit = st.form_submit_button("Save Info")

    if submit:
        user_info = {
            "name": name,
            "dob": dob,
            "birth_place": birth_place,
            "birth_time": birth_time,
            "gender": gender,
            "mood": mood,
            "day_summary": day_summary,
        }
        st.session_state.user_info = user_info
        st.session_state.language = language
        st.success("User info saved successfully!")

# Save PDF
        os.makedirs("user_logs", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="TarotTara User Log", ln=True, align="C")
        pdf.ln(10)
        for key, value in user_info.items():
            pdf.cell(200, 10, txt=f"{key.title()}: {value}", ln=True)
        filename = f"user_logs/{name.replace(' ', '_')}_log.pdf"
        pdf.output(filename)

# Main app input section
st.subheader("🧘 Ask your question")
input_method = st.radio("Choose input method", ["Type", "Upload Audio"])

question = ""
if input_method == "Type":
    question = st.text_area("Type your question below:")
elif input_method == "Upload Audio":
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    if audio_file:
        with st.spinner("Transcribing your audio..."):
            question = transcribe_audio(audio_file)
            st.success(f"✅ You said: {question}")

if st.button("🔮 Submit Question") and question:
    with st.spinner("Analyzing your question..."):
        detected_lang = detect(question)
        translated_question = GoogleTranslator(source='auto', target='en').translate(question) if detected_lang != "en" else question

        intent_start = time.time()
        intent = classify_intent_cached(translated_question)
        intent_duration = time.time() - intent_start

        prediction_start = time.time()
        result = cached_reading(translated_question, intent)
        prediction_duration = time.time() - prediction_start

        if "error" in result:
            st.error(f"⚠️ Error: {result['error']}")
        else:
            answer_en = result["interpretation"]
            user_lang = st.session_state.language
            final_answer = GoogleTranslator(source='en', target=user_lang).translate(answer_en) if user_lang != "en" else answer_en

            st.markdown("### 🔍 TarotTara says:")
            if intent == "timeline":
                card = result.get("card", "")
                date_range = result.get("date_range", ["", ""])
                st.write(f"**Card:** {card}")
                st.write(f"**Timeframe:** {date_range[0].strftime('%B %d')} – {date_range[1].strftime('%B %d')}")

            elif intent == "factual":
                st.write("**Answer:**")
            else:
                cards = result.get("cards", [])
                if cards:
                    st.write(f"**Cards Drawn:** {', '.join(cards)}")

            st.success(final_answer)

            # audio_path = synthesize_voice(final_answer, user_input_lang=user_lang)
            # if audio_path and os.path.exists(audio_path):
            #     audio_bytes = open(audio_path, 'rb').read()
            #     st.audio(audio_bytes, format='audio/mp3')

            st.markdown(f"⏱️ **Intent classification:** {intent_duration:.2f}s")
            st.markdown(f"⏱️ **Prediction (LLM + RAG):** {prediction_duration:.2f}s")
