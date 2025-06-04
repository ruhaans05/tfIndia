
import streamlit as st
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import openai
from datetime import datetime

# === Load API Key ===
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("No OpenAI API key found in environment.")
    st.stop()
openai.api_key = api_key

# === File for storing chat history and users ===
CHAT_LOG = ROOT / "chat_log.json"
USER_DB = ROOT / "chat_users.json"

if not USER_DB.exists():
    with open(USER_DB, "w") as f:
        json.dump({}, f)

if not CHAT_LOG.exists():
    with open(CHAT_LOG, "w") as f:
        json.dump([], f)

# === Utility Functions ===
def load_users():
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

def load_chat():
    with open(CHAT_LOG, "r") as f:
        return json.load(f)

def save_chat(messages):
    with open(CHAT_LOG, "w") as f:
        json.dump(messages, f)

def censor_text(text):
    banned = ["fuck", "shit", "bitch", "asshole", "nigga", "cunt", "retard", "dick"]
    for word in banned:
        text = text.replace(word, "***")
    return text

# === Sidebar Chat ===
with st.sidebar:
    st.header("Live Chatroom")
    chat_users = load_users()

    if "chat_user" not in st.session_state:
        st.session_state.chat_user = None

    if st.session_state.chat_user:
        st.success(f"Logged in as {st.session_state.chat_user}")
    else:
        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            uname = st.text_input("Username", key="login_user")
            pwd = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if uname in chat_users and chat_users[uname] == pwd:
                    st.session_state.chat_user = uname
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        with register_tab:
            new_user = st.text_input("New Username", key="new_user")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            if st.button("Register"):
                if new_user in chat_users:
                    st.warning("Username already taken.")
                elif new_user.strip() == "" or new_pass.strip() == "":
                    st.warning("Username and password cannot be empty.")
                else:
                    chat_users[new_user] = new_pass
                    save_users(chat_users)
                    st.session_state.chat_user = new_user
                    st.rerun()

    if st.session_state.chat_user:
        all_msgs = load_chat()
        visible_msgs = []
        for msg in all_msgs[-50:]:
            is_private = msg['msg'].startswith("@")
            mentioned_user = msg['msg'].split()[0][1:] if is_private else None
            if not is_private or mentioned_user == st.session_state.chat_user or msg["user"] == st.session_state.chat_user:
                visible_msgs.append(msg)

        for msg in visible_msgs:
            st.markdown(f"**{msg['user']}**: {msg['msg']}")

        new_msg = st.text_input("Type your message", key="chat_input")
        if st.button("Send"):
            if new_msg.strip():
                clean_msg = censor_text(new_msg.strip())
                all_msgs.append({"user": st.session_state.chat_user, "msg": clean_msg, "time": str(datetime.now())})
                save_chat(all_msgs)
                st.rerun()

# === Main Prompt Globalizer ===
st.title("TraceForge — Prompt Globalizer")
st.caption("Bridge global divides by translating and rewriting prompts for different audiences")

if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = None
if "code_output" not in st.session_state:
    st.session_state.code_output = None
if "code_explanation" not in st.session_state:
    st.session_state.code_explanation = None

st.subheader("Enter Your Prompt")
user_prompt = st.text_area("Prompt", height=120, placeholder="Enter your prompt...")

st.subheader("Global Targeting Options")
col1, col2 = st.columns(2)
with col1:
    target = st.selectbox("Target Audience Region", ["India", "United States", "Europe", "Middle East", "Africa", "Southeast Asia"])
    tone = st.selectbox("Desired Tone", ["Professional", "Casual", "Academic", "Persuasive", "Youth-Oriented"])
with col2:
    language = st.selectbox("Output Language", ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Gujarati", "Kannada", "Punjabi", "Marathi", "Urdu"])
    localize = st.checkbox("Localize for Infrastructure Constraints", value=True)

if st.button("Globalize Prompt"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Rewriting prompt..."):
            system_msg = f"""
You are an expert at prompt localization. Rewrite prompts so that they are understandable, culturally appropriate, and optimized for people in {target}.
The tone should be {tone.lower()} and the output language should be {language}.
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

if st.session_state.final_prompt:
    st.subheader("Localized Prompt")
    st.text_area("Rewritten Prompt", value=st.session_state.final_prompt, height=200, key="final_prompt_display")

    st.markdown("---")
    st.subheader("Region-Optimized Pipeline Starter Code")

    if target == "India":
        infra_region = st.selectbox("Target Subregion (India Infrastructure Preset)", [
            "Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Kerala", "Hyderabad",
            "Gangetic Plain — Rural Bihar/UP", "North-East India", "Rajasthan",
            "Punjab/Haryana", "Tier 2 Towns",
        ])
    else:
        infra_region = target

    explain_in_lang = st.checkbox("Show explanation in selected language", value=True)
    explain_lang = st.selectbox("Explanation Language", ["English", "Hindi", "Marathi", "Tamil", "Telugu", "Bengali", "Malayalam", "Gujarati", "Kannada", "Punjabi", "Urdu"]) if explain_in_lang else None

    if st.button("Generate Code for This Prompt"):
        with st.spinner("Generating code..."):
            code_system_prompt = f"You are a senior AI engineer. Generate a starter pipeline in Python for the following prompt, geared toward the {infra_region} environment. The tone should be {tone.lower()}, and the primary language should be {language}."
            if localize:
                code_system_prompt += " Adapt the code for regional infrastructure such as mobile-first use or low-bandwidth."

            code_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": code_system_prompt},
                    {"role": "user", "content": st.session_state.final_prompt}
                ],
                temperature=0.6
            )
            st.session_state.code_output = code_response.choices[0].message.content
            st.session_state.code_explanation = None

            if explain_in_lang and explain_lang:
                with st.spinner("Translating explanation..."):
                    explain_prompt = f"Explain the following Python pipeline to a user in {infra_region}. Use {explain_lang} and keep it beginner-friendly.\n\n{st.session_state.code_output}"
                    explain_response = openai.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": f"You are a helpful programming tutor who explains code clearly in {explain_lang}."},
                            {"role": "user", "content": explain_prompt}
                        ],
                        temperature=0.4
                    )
                    st.session_state.code_explanation = explain_response.choices[0].message.content

if st.session_state.code_output:
    st.code(st.session_state.code_output, language="python")
    if st.session_state.code_explanation:
        st.subheader("Code Explanation")
        st.markdown(st.session_state.code_explanation)
    st.markdown("This pipeline is a regional starting point — customize as needed.")
