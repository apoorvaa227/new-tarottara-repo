import os
import time
import streamlit as st
from fpdf import FPDF
from langdetect import detect
from deep_translator import GoogleTranslator
from intent.intent import classify_intent_cached
from tarot.tarot_reader import cached_reading
from voice_utils import transcribe_audio, synthesize_voice

# --- Config ---
st.set_page_config(page_title="Tarot AI - Your Magical Guide", layout="centered")
st.title("🔮 Tarot AI – Your Magical Tarot Guide")

# --- Session State Init ---
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

if "language" not in st.session_state:
    st.session_state.language = "en"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar for User Info ---
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
        st.session_state.user_info = {
            "name": name,
            "dob": dob,
            "birth_place": birth_place,
            "birth_time": birth_time,
            "gender": gender,
            "mood": mood,
            "day_summary": day_summary,
        }
        st.session_state.language = language
        st.success("User info saved!")

        # Save PDF log
        os.makedirs("user_logs", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="TarotTara User Log", ln=True, align="C")
        pdf.ln(10)
        for key, value in st.session_state.user_info.items():
            pdf.cell(200, 10, txt=f"{key.title()}: {value}", ln=True)
        filename = f"user_logs/{name.replace(' ', '_')}_log.pdf"
        pdf.output(filename)

# --- Chat Interface ---
st.subheader("💬 Chat with TarotTara")

# Display past messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input
user_input = st.chat_input("Ask your tarot question...")

if user_input:
    # Show user input
    st.chat_message("user").markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Process
    with st.spinner("Let me consult the tarot..."):
        detected_lang = detect(user_input)
        translated_question = GoogleTranslator(source='auto', target='en').translate(user_input) if detected_lang != "en" else user_input

        # Intent classification
        intent_start = time.time()
        intent = classify_intent_cached(translated_question)
        intent_duration = time.time() - intent_start

        # Tarot reading
        prediction_start = time.time()
        result = cached_reading(translated_question, intent)
        prediction_duration = time.time() - prediction_start

        # Final response
        if "error" in result:
            bot_reply = f"⚠️ Error: {result['error']}"
        else:
            answer_en = result["interpretation"]
            user_lang = st.session_state.language
            final_answer = GoogleTranslator(source='en', target=user_lang).translate(answer_en) if user_lang != "en" else answer_en

            # Include details (cards, timeline) if relevant
            details = ""
            if intent == "timeline":
                card = result.get("card", "")
                date_range = result.get("date_range", ["", ""])
                details += f"**Card:** {card}\n\n"
                details += f"**Timeframe:** {date_range[0].strftime('%B %d')} – {date_range[1].strftime('%B %d')}\n\n"
            elif intent != "yes_no":
                cards = result.get("cards", [])
                if cards:
                    details += f"**Cards Drawn:** {', '.join(cards)}\n\n"

            bot_reply = f"{details}{final_answer}"

        # Show and store reply
        st.chat_message("assistant").markdown(bot_reply)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

        # Optional: Voice Output
        audio_path = synthesize_voice(final_answer, user_input_lang=user_lang)
        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format="audio/mp3")

        # Timing info
        st.caption(f"⏱️ Intent classification: {intent_duration:.2f}s")
        st.caption(f"⏱️ Prediction (LLM + RAG): {prediction_duration:.2f}s")
