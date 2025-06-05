import streamlit as st
import openai

st.set_page_config(page_title="USGateway — Tech Jobs for Indians")

st.title("💼 USGateway — Break Into the American Tech Scene")
st.caption("A personalized tool for Indian techies to land U.S. jobs and internships.")

lang = st.selectbox("Choose your preferred language", ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Bengali", "Gujarati", "Marathi", "Urdu"])

st.markdown("### 🧑‍💻 Your Tech Background")
col1, col2 = st.columns(2)
with col1:
    degree = st.selectbox("Your degree/background", ["Computer Science", "Data Science", "Electronics", "Other"])
    experience = st.selectbox("Experience Level", ["Student", "0–1 years", "1–3 years", "3+ years"])
with col2:
    role = st.selectbox("Target U.S. Role", ["Software Engineer", "Data Scientist", "Backend Developer", "ML Engineer", "Product Manager", "Other"])
    location = st.selectbox("Current City", ["Bangalore", "Mumbai", "Hyderabad", "Delhi", "Chennai", "Tier 2/3 City", "Abroad"])

st.markdown("### 🛠️ Skills")
skills = st.multiselect("Select your core skills", ["Python", "SQL", "C++", "Java", "React", "Node.js", "TensorFlow", "Pandas", "AWS", "Docker"])

st.markdown("### 📝 Get Recruiter-Ready")
resume_summary = st.text_area("Paste your current resume or job summary (optional)", height=150)

if st.button("Generate My U.S. Prep Plan"):
    with st.spinner("Analyzing your profile and generating a tailored plan..."):
        prep_prompt = f'''
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
'''
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
