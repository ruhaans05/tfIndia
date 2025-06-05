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
    banned = ["fuck", "shit", "bitch", "asshole", "nigga", "cunt", "retard", "dick", "nigger"]
    for word in banned:
        text = text.replace(word, "***")
    return text

# === Sidebar Chat ===
with st.sidebar:
    st.header("Live Chatroom \n(Connect with Developers Around the World)\n\n@username to private message")
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
        for msg in all_msgs[-50:]:
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

st.subheader("Enter Your Prompt\nAsk the model a question, and write code for it with explanations!")
input_mode = st.radio("Choose input method:", ["Typing", "Voice (Upload)"], index=0, horizontal=True)

if input_mode == "Typing":
    user_prompt = st.text_area("Prompt", height=120, placeholder="Enter your prompt...")
else:
    import tempfile
    import whisper

    audio_file = st.file_uploader("Upload your voice prompt (WAV/MP3)", type=["wav", "mp3"])
    user_prompt = ""

    if audio_file is not None:
        with st.spinner("Transcribing audio..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_file_path = tmp_file.name

            model = whisper.load_model("base")
            result = model.transcribe(tmp_file_path)
            user_prompt = result["text"]
            st.success("Transcription complete.")
            st.text_area("Transcribed Prompt", value=user_prompt, height=120, key="transcribed_prompt")

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
            code_system_prompt = f"You are a senior AI engineer. Generate a starter pipeline in Python for the following prompt, The tone should be {tone.lower()}, and the primary language should be {language}."
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
                    explain_prompt = f"Explain the following Python pipeline to a user in the selected region. Use {explain_lang} and keep it beginner-friendly.\n\n{st.session_state.code_output}"
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



# === USGateway Add-on ===
st.markdown("---")
st.title("💼 USGateway — Break Into the American Tech Scene")
st.caption("A personalized tool for Indian techies to land U.S. jobs and internships.")

lang = st.selectbox("Choose your preferred language", ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Bengali", "Gujarati", "Marathi", "Urdu"], key="us_lang")

st.markdown("### 🧑‍💻 Your Tech Background")
col1, col2 = st.columns(2)
with col1:
    degree = st.selectbox("Your degree/background", ["Computer Science", "Data Science", "Electronics", "Other"], key="us_degree")
    experience = st.selectbox("Experience Level", ["Student", "0–1 years", "1–3 years", "3+ years"], key="us_exp")
with col2:
    role = st.selectbox("Target U.S. Role", ["Software Engineer", "Data Scientist", "Backend Developer", "ML Engineer", "Product Manager", "Other"], key="us_role")
    location = st.selectbox("Current City", ["Bangalore", "Mumbai", "Hyderabad", "Delhi", "Chennai", "Tier 2/3 City", "Abroad"], key="us_loc")

st.markdown("### 🛠️ Skills")
skills = st.multiselect("Select your core skills", ["Python", "SQL", "C++", "Java", "React", "Node.js", "TensorFlow", "Pandas", "AWS", "Docker"], key="us_skills")

st.markdown("### 📝 Get Recruiter-Ready")
resume_summary = st.text_area("Paste your current resume or job summary (optional)", height=150, key="us_resume")

if st.button("Generate My U.S. Prep Plan", key="us_button"):
    with st.spinner("Analyzing your profile and generating a tailored plan..."):
        prep_prompt = f"""
You are a career coach helping Indian students and professionals break into the U.S. tech job market.
Language: {lang}
Degree: {degree}
Experience: {experience}
Target Role: {role}
Current City: {location}
Skills: {', '.join(skills)}
Resume Summary: {resume_summary if resume_summary.strip() else "Not provided"}

Give a realistic readiness score out of 100, then list:
1. 3 major steps to improve profile
2. U.S.-style resume bullet examples
3. One sample cold email to a recruiter
4. Key interview areas to focus on
Use simple, motivating language — translate all to {lang}.
"""
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are a bilingual career coach giving personalized advice in {lang}."},
                {"role": "user", "content": prep_prompt}
            ],
            temperature=0.6
        )
        st.markdown("### 🎯 Your U.S. Job Plan")
        st.markdown(response.choices[0].message.content)
