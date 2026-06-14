import streamlit as st
from deep_translator import GoogleTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
import speech_recognition as sr
from textblob import TextBlob
import pytesseract
from PIL import Image
import os
import logging
logging.disable(logging.WARNING)

# ── Language setup ──
LANG_LIST = {k.title(): v for k, v in GOOGLE_LANGUAGES_TO_CODES.items()}
LANG_NAMES = sorted(LANG_LIST.keys())

# ── Page Config ──
st.set_page_config(
    page_title="🌍 Global Translator Pro",
    page_icon="🌍",
    layout="wide"
)

# ── Session State ──
for key in ["input_text", "translated_text", "chat_history"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "chat_history" else []

# ── Title ──
st.title("🌍 Global Translator Pro")
st.caption("The most powerful translator — Multi-language, Emotion Detection, Image & Chat!")
st.divider()

# ── TABS ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✏️ Translate",
    "🔄 Multi-Language",
    "😊 Emotion Detection",
    "🖼️ Image to Text",
    "💬 Chat Translator"
])

# ══════════════════════════════════════
# TAB 1 — Basic Translate + Voice
# ══════════════════════════════════════
with tab1:
    st.subheader("✏️ Text & Voice Translator")

    input_method = st.radio("Input method:", ["Type Text", "🎤 Voice Input"], horizontal=True)

    if input_method == "Type Text":
        st.session_state.input_text = st.text_area(
            "Enter text:", height=150,
            placeholder="Type anything here..."
        )
    else:
        if st.button("🎤 Start Listening", use_container_width=True):
            ph = st.empty()
            ph.warning("🎤 Listening... Speak now!")
            try:
                r = sr.Recognizer()
                r.energy_threshold = 300
                r.dynamic_energy_threshold = False
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1)
                    audio = r.listen(source, timeout=6, phrase_time_limit=10)
                text = r.recognize_google(audio)
                st.session_state.input_text = text
                ph.success(f"✅ Captured: **{text}**")
            except sr.WaitTimeoutError:
                ph.error("❌ No speech detected!")
            except sr.UnknownValueError:
                ph.error("❌ Could not understand audio!")
            except Exception as e:
                ph.error(f"❌ Error: {e}")

        if st.session_state.input_text:
            st.text_area("Voice Text:", value=st.session_state.input_text,
                         height=100, disabled=True)

    target_lang = st.selectbox("Translate to:", LANG_NAMES, key="tab1_lang")

    if st.button("🌐 Translate", use_container_width=True, type="primary", key="tab1_btn"):
        if not st.session_state.input_text.strip():
            st.warning("⚠️ Please enter some text!")
        else:
            with st.spinner("Translating..."):
                try:
                    result = GoogleTranslator(
                        source="auto",
                        target=LANG_LIST[target_lang]
                    ).translate(st.session_state.input_text)
                    st.session_state.translated_text = result
                    st.success("✅ Translation Done!")
                    st.text_area("Result:", value=result, height=150)
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ══════════════════════════════════════
# TAB 2 — Multi Language at Once
# ══════════════════════════════════════
with tab2:
    st.subheader("🔄 Translate into Multiple Languages at Once!")
    st.caption("Type once — get translation in 5 languages simultaneously!")

    multi_text = st.text_area("Enter text to translate:", height=150,
                               placeholder="Type anything here...", key="multi_input")

    default_langs = ["Tamil", "Hindi", "French", "Spanish", "Arabic"]
    selected_langs = st.multiselect(
        "Choose languages (pick up to 10):",
        LANG_NAMES,
        default=default_langs
    )

    if st.button("🔄 Translate All", use_container_width=True, type="primary", key="multi_btn"):
        if not multi_text.strip():
            st.warning("⚠️ Please enter some text!")
        elif not selected_langs:
            st.warning("⚠️ Please select at least one language!")
        else:
            st.divider()
            st.subheader("🌍 Translations")
            cols = st.columns(2)
            for i, lang in enumerate(selected_langs):
                with st.spinner(f"Translating to {lang}..."):
                    try:
                        result = GoogleTranslator(
                            source="auto",
                            target=LANG_LIST[lang]
                        ).translate(multi_text)
                        with cols[i % 2]:
                            st.markdown(f"**🌐 {lang}**")
                            st.success(result)
                    except Exception as e:
                        with cols[i % 2]:
                            st.error(f"❌ {lang}: {e}")

# ══════════════════════════════════════
# TAB 3 — Emotion & Sentiment Detection
# ══════════════════════════════════════
with tab3:
    st.subheader("😊 Emotion & Sentiment Detection")
    st.caption("Detects the mood of your text BEFORE translating!")

    emotion_text = st.text_area("Enter text to analyze:", height=150,
                                 placeholder="Type something...", key="emotion_input")

    target_lang_emotion = st.selectbox("Also translate to:", LANG_NAMES, key="emotion_lang")

    if st.button("😊 Detect & Translate", use_container_width=True,
                 type="primary", key="emotion_btn"):
        if not emotion_text.strip():
            st.warning("⚠️ Please enter some text!")
        else:
            with st.spinner("Analyzing emotion..."):

                # ── Sentiment Analysis ──
                blob = TextBlob(emotion_text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity

                # ── Emotion Label ──
                if polarity > 0.5:
                    emotion = "😄 Very Positive / Happy"
                    color = "green"
                elif polarity > 0:
                    emotion = "🙂 Slightly Positive"
                    color = "green"
                elif polarity == 0:
                    emotion = "😐 Neutral"
                    color = "blue"
                elif polarity > -0.5:
                    emotion = "😟 Slightly Negative"
                    color = "orange"
                else:
                    emotion = "😢 Very Negative / Sad"
                    color = "red"

                # ── Subjectivity Label ──
                if subjectivity > 0.6:
                    subj_label = "💭 Very Opinionated"
                elif subjectivity > 0.3:
                    subj_label = "🤔 Somewhat Opinionated"
                else:
                    subj_label = "📰 Factual / Objective"

                st.divider()
                st.subheader("📊 Emotion Analysis Result")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("😊 Emotion", emotion)
                with col2:
                    st.metric("📈 Polarity Score", f"{polarity:.2f}")
                with col3:
                    st.metric("💭 Subjectivity", subj_label)

                # ── Sentiment Bar ──
                st.markdown("**Sentiment Scale:** Negative ◀️ ─────── ▶️ Positive")
                st.progress((polarity + 1) / 2)

                # ── Translation ──
                st.divider()
                try:
                    translated = GoogleTranslator(
                        source="auto",
                        target=LANG_LIST[target_lang_emotion]
                    ).translate(emotion_text)
                    st.subheader(f"🌐 Translated to {target_lang_emotion}")
                    st.success(translated)
                except Exception as e:
                    st.error(f"❌ Translation Error: {e}")

# ══════════════════════════════════════
# TAB 4 — Image to Text & Translate
# ══════════════════════════════════════
with tab4:
    st.subheader("🖼️ Image to Text & Translate")
    st.caption("Upload an image containing text — we extract and translate it!")

    uploaded_image = st.file_uploader(
        "Upload Image (JPG, PNG):",
        type=["jpg", "jpeg", "png"]
    )

    target_lang_img = st.selectbox("Translate extracted text to:", LANG_NAMES, key="img_lang")

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("🔍 Extract & Translate", use_container_width=True,
                     type="primary", key="img_btn"):
            with st.spinner("Extracting text from image..."):
                try:
                    extracted = pytesseract.image_to_string(image).strip()

                    if not extracted:
                        st.warning("⚠️ No text found in image! Try a clearer image.")
                    else:
                        st.divider()
                        st.subheader("📝 Extracted Text")
                        st.info(extracted)

                        with st.spinner("Translating..."):
                            translated = GoogleTranslator(
                                source="auto",
                                target=LANG_LIST[target_lang_img]
                            ).translate(extracted)

                            st.subheader(f"🌐 Translated to {target_lang_img}")
                            st.success(translated)

                except Exception as e:
                    st.error(f"❌ Error: {e}\n\nMake sure Tesseract is installed!")
                    st.info("📥 Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")

# ══════════════════════════════════════
# TAB 5 — Real Time Chat Translator
# ══════════════════════════════════════
with tab5:
    st.subheader("💬 Real Time Chat Translator")
    st.caption("Two people chat in different languages and understand each other!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👤 Person 1")
        p1_lang = st.selectbox("Person 1 Language:", LANG_NAMES,
                                index=LANG_NAMES.index("English"), key="p1_lang")
        p1_msg = st.text_input("Person 1 message:", placeholder="Type here...", key="p1_msg")
        p1_send = st.button("📤 Send", key="p1_send", use_container_width=True)

    with col2:
        st.markdown("### 👥 Person 2")
        p2_lang = st.selectbox("Person 2 Language:", LANG_NAMES,
                                index=LANG_NAMES.index("Tamil"), key="p2_lang")
        p2_msg = st.text_input("Person 2 message:", placeholder="Type here...", key="p2_msg")
        p2_send = st.button("📤 Send", key="p2_send", use_container_width=True)

    # ── Person 1 sends ──
    if p1_send and p1_msg.strip():
        with st.spinner("Translating..."):
            try:
                translated = GoogleTranslator(
                    source="auto",
                    target=LANG_LIST[p2_lang]
                ).translate(p1_msg)
                st.session_state.chat_history.append({
                    "sender": f"👤 Person 1 ({p1_lang})",
                    "original": p1_msg,
                    "translated": translated,
                    "target_lang": p2_lang
                })
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ── Person 2 sends ──
    if p2_send and p2_msg.strip():
        with st.spinner("Translating..."):
            try:
                translated = GoogleTranslator(
                    source="auto",
                    target=LANG_LIST[p1_lang]
                ).translate(p2_msg)
                st.session_state.chat_history.append({
                    "sender": f"👥 Person 2 ({p2_lang})",
                    "original": p2_msg,
                    "translated": translated,
                    "target_lang": p1_lang
                })
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ── Chat History ──
    if st.session_state.chat_history:
        st.divider()
        st.subheader("💬 Chat History")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**{chat['sender']}:** {chat['original']}")
            st.success(f"🌐 Translated to {chat['target_lang']}: {chat['translated']}")
            st.markdown("---")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ── Footer ──
st.divider()
st.markdown("<center>🌍 Global Translator Pro — Made with ❤️ using Python & Streamlit</center>",
            unsafe_allow_html=True)
