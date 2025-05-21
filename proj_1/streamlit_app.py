import streamlit as st
from PyPDF2 import PdfReader

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="AI Resume Parser with Fast Skill Extraction", layout="wide")

# Set of common technical and soft skills
full_skill_list = [
    "Python", "Java", "C++", "SQL", "JavaScript", "React", "Node.js", "Django", "Flask",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Machine Learning",
    "Deep Learning", "NLP", "Data Science", "TensorFlow", "PyTorch", "Agile", "Scrum",
    "Project Management", "Leadership", "Problem Solving", "Communication",
    "Team Management", "Risk Management", "Time Management"
]

# -------- Helper functions --------

def extract_text_from_pdf(uploaded_file, max_pages=2):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for i, page in enumerate(pdf_reader.pages):
        if i >= max_pages:
            break
        text += page.extract_text() or ""
    return text

def extract_skills(text):
    text_lower = text.lower()
    return [skill for skill in full_skill_list if skill.lower() in text_lower]

def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0
    matched = [skill for skill in resume_skills if skill in jd_skills]
    return round(len(matched) / len(jd_skills) * 100, 2)

# -------- UI layout --------

st.title("📄 Resume Matcher")

st.sidebar.header("Upload Resumes")
uploaded_resumes = st.sidebar.file_uploader("Upload PDF resumes", type="pdf", accept_multiple_files=True)

st.sidebar.header("Job Description")
jd_text = st.sidebar.text_area("Paste the job description here")

if uploaded_resumes and jd_text:
    if st.button("Run Matching"):
        # Extract JD skills once
        jd_skills = extract_skills(jd_text)

        for i, resume_file in enumerate(uploaded_resumes, start=1):
            with st.spinner(f"Analyzing Resume {i}..."):
                resume_text = extract_text_from_pdf(resume_file)
                resume_skills = extract_skills(resume_text)
                match_score = calculate_match_score(resume_skills, jd_skills)

                st.subheader(f"Resume {i} - Match Score")
                st.metric(label=resume_file.name, value=f"{match_score}%")
else:
    st.warning("Please upload at least one resume and enter a job description.")
