import streamlit as st
from PyPDF2 import PdfReader
from transformers import pipeline

@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_classifier()

candidate_labels = [
    "project management", "engineering", "leadership", "planning", "execution",
    "budgeting", "technical teams", "problem-solving", "communication",
    "team management", "agile", "scrum", "time management", "risk management"
]

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_skills_from_resume(text):
    text = text.lower()
    found_skills = []
    for skill in candidate_labels:
        if skill.lower() in text:
            found_skills.append(skill)
    return list(set(found_skills))

def extract_keywords_from_jd(jd_text):
    result = classifier(jd_text, candidate_labels, multi_label=True)
    extracted = [label for label, score in zip(result['labels'], result['scores']) if score > 0.6]
    return extracted


def calculate_match_score(resume_skills, jd_keywords):
    if not jd_keywords:
        return 0.0
    matched = [skill for skill in resume_skills if skill in jd_keywords]
    return round(len(matched) / len(jd_keywords) * 100, 2)


st.title("📄 AI Resume Parser")

st.sidebar.header("Upload Resumes")
uploaded_resumes = st.sidebar.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

st.sidebar.header("Job Description")
jd_text = st.sidebar.text_area("Paste the job description here")

if uploaded_resumes and jd_text:
    with st.spinner("🔍 Analyzing resumes and JD..."):
        jd_keywords = extract_keywords_from_jd(jd_text)
        for i, uploaded_resume in enumerate(uploaded_resumes, start=1):
            resume_text = extract_text_from_pdf(uploaded_resume)
            resume_skills = extract_skills_from_resume(resume_text)
            score = calculate_match_score(resume_skills, jd_keywords)

            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.subheader(f"✅ Match Score for Resume {i}:")
                st.metric(label="Match %", value=f"{score}%")
            with col2:
                st.markdown(f"**File:** `{uploaded_resume.name}`")
else:
    st.warning("📤 Please upload one or more resumes and paste a job description to continue.")
