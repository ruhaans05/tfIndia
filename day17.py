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
st.title("🌐 TraceForge — Prompt Globalizer (Day 17)")
st.caption("Bridge global divides by translating and rewriting prompts for different audiences")

# === Session State Setup ===
if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = None
if "code_output" not in st.session_state:
    st.session_state.code_output = None

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

# === Show Final Prompt ===
if st.session_state.final_prompt:
    st.success("✅ Prompt localized successfully!")
    st.subheader("🌟 Localized Prompt")
    st.text_area("Rewritten Prompt", value=st.session_state.final_prompt, height=200, key="final_prompt_display")

    st.markdown("---")
    st.subheader("🔧 Region-Optimized Pipeline Starter Code")

    if st.button("🛠 Generate Code for This Prompt"):
        with st.spinner("Engineering a pipeline that fits this region..."):
            code_system_prompt = (
                f"You are a senior AI engineer. Generate a starter pipeline in Python "
                f"for the following prompt, geared toward the {target.lower()} audience. The tone should be {tone.lower()}, "
                f"and the primary language should be {language}."
            )
            if localize:
                code_system_prompt += (
                    " Add considerations for regional infrastructure — like mobile-first UX, edge computing, or low-connectivity resilience."
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

# === Show Code Output ===
if st.session_state.code_output:
    st.code(st.session_state.code_output, language="python")
    st.markdown("🧠 **Note:** This pipeline is a regional starting point — feel free to swap out libraries or integrate APIs as needed.")
