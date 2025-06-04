import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import openai

# === Load API Key ===
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ No OpenAI API key found in environment.")
    st.stop()
openai.api_key = api_key

# === Page Setup ===
st.set_page_config(page_title="🌐 Prompt Globalizer", layout="centered")
st.title("🌐 TraceForge — Prompt Globalizer")
st.caption("Bridge global divides by translating and rewriting prompts for different audiences")

# === Session State Setup ===
if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = None
if "code_output" not in st.session_state:
    st.session_state.code_output = None
if "code_explanation" not in st.session_state:
    st.session_state.code_explanation = None

# === Prompt Input ===
st.subheader("📝 Enter Your Prompt")
user_prompt = st.text_area("Prompt", height=120, placeholder="Enter your prompt in English or another language...")

# === Localization Options ===
st.subheader("🌍 Global Targeting Options")
col1, col2 = st.columns(2)
with col1:
    target = st.selectbox("🌐 Target Audience Region", ["India", "United States", "Europe", "Middle East", "Africa", "Southeast Asia"])
    tone = st.selectbox("🎯 Desired Tone", ["Professional", "Casual", "Academic", "Persuasive", "Youth-Oriented"])
with col2:
    language = st.selectbox("🗣 Output Language", ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Gujarati", "Kannada", "Punjabi", "Marathi", "Urdu"])
    localize = st.checkbox("⚙️ Localize for Infrastructure Constraints (e.g., mobile-first, low bandwidth)", value=True)

# === Prompt Rewriting ===
if st.button("🌐 Globalize Prompt"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Rewriting prompt for target region..."):
            system_msg = f"""
You are an expert at prompt localization. Rewrite prompts so that they are understandable, culturally appropriate, and optimized for people in {target}.
The tone should be {tone.lower()} and the output language should be {language}.
Ensure it works well for people in that region and adjust terms, references, or phrasing to feel native and relevant.
"""
            if localize:
                system_msg += " Consider local infrastructure issues like mobile-first usage, spotty internet, or edge devices."

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )
            st.session_state.final_prompt = response.choices[0].message.content
            st.session_state.code_output = None
            st.session_state.code_explanation = None

# === Show Final Prompt ===
if st.session_state.final_prompt:
    st.success("✅ Prompt localized successfully!")
    st.subheader("🌟 Localized Prompt")
    st.text_area("Rewritten Prompt", value=st.session_state.final_prompt, height=200, key="final_prompt_display")

    st.markdown("---")
    st.subheader("🔧 Region-Optimized Pipeline Starter Code")

    # === Subregion Selector for India ===
    if target == "India":
        infra_region = st.selectbox("🧠 Target Subregion (India Infrastructure Preset)", [
            "Delhi",
            "Mumbai",
            "Bangalore",
            "Kolkata",
            "Chennai",
            "Kerala",
            "Hyderabad",
            "Gangetic Plain — Rural Bihar/UP",
            "North-East India",
            "Rajasthan",
            "Punjab/Haryana",
            "Tier 2 Towns",
        ])
    else:
        infra_region = target  # fallback to global region

    explain_in_lang = st.checkbox("🈯 Show explanation in selected language", value=True)

    if explain_in_lang:
        explain_lang = st.selectbox("🌐 Explanation Language", [
            "English", "Hindi", "Marathi", "Tamil", "Telugu", "Bengali",
            "Malayalam", "Gujarati", "Kannada", "Punjabi", "Urdu"
        ])
    else:
        explain_lang = None

    if st.button("🛠 Generate Code for This Prompt"):
        with st.spinner("Engineering a pipeline that fits this region..."):
            code_system_prompt = (
                f"You are a senior AI engineer. Generate a starter pipeline in Python "
                f"for the following prompt, geared toward the {infra_region} environment. "
                f"The tone should be {tone.lower()}, and the primary language should be {language}."
            )
            if localize:
                code_system_prompt += (
                    " Adapt the code for regional infrastructure — for example, low-bandwidth resilience, "
                    "on-device inference, or mobile-first interactions where needed."
                )

            code_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": code_system_prompt},
                    {"role": "user", "content": st.session_state.final_prompt}
                ],
                temperature=0.6,
            )
            st.session_state.code_output = code_response.choices[0].message.content
            st.session_state.code_explanation = None

            # Generate code explanation if enabled
            if explain_in_lang and explain_lang:
                with st.spinner("Translating code explanation..."):
                    explain_prompt = (
                        f"Explain the following Python pipeline to a user in {infra_region}. "
                        f"Use {explain_lang} and keep the explanation concise, clear, and beginner-friendly.\n\n"
                        f"{st.session_state.code_output}"
                    )
                    explain_response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": f"You are a helpful programming tutor who explains code clearly in {explain_lang}."},
                            {"role": "user", "content": explain_prompt}
                        ],
                        temperature=0.4,
                    )
                    st.session_state.code_explanation = explain_response.choices[0].message.content

# === Show Code Output ===
if st.session_state.code_output:
    st.code(st.session_state.code_output, language="python")
    if st.session_state.code_explanation:
        st.subheader("📘 Code Explanation")
        st.markdown(st.session_state.code_explanation)
    st.markdown("🧠 **Note:** This pipeline is a regional starting point — feel free to swap out libraries or integrate APIs as needed.")

# === Live Global Chat (Sidebar) ===
with st.sidebar.expander("💬 Open Global Chat"):
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    def filter_profanity(text):
        bad_words = {"fuck", "shit", "bitch", "ass", "nigga", "faggot", "dick", "pussy", "cunt"}
        for word in bad_words:
            text = text.replace(word, "[filtered]")
        return text

    name = st.text_input("Your Name", value="Anonymous")
    message = st.text_input("Type your message")

    if st.button("Send"):
        if message.strip():
            clean_msg = filter_profanity(message.strip())
            full_msg = f"**{name.strip()}**: {clean_msg}"
            st.session_state.chat_log.insert(0, full_msg)

    st.markdown("---")
    st.markdown("### 🌐 Chat History")
    for msg in st.session_state.chat_log:
        st.markdown(msg)

