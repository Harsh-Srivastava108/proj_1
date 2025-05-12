import streamlit as st
import pandas as pd
import tempfile
import os
import re
import pdfplumber
import spacy
from spacy.matcher import PhraseMatcher
import io

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Skill, education, experience keywords
SKILLS_DB = ["python", "java", "c++", "sql", "javascript", "html", "css",
             "machine learning", "deep learning", "nlp", "data analysis", "excel", "communication"]
EDUCATION_KEYWORDS = ["bachelor", "master", "b.sc", "m.sc", "b.tech", "m.tech", "ph.d", "mba", "bca", "mca"]
EXPERIENCE_KEYWORDS = ["intern", "developer", "engineer", "manager", "analyst", "consultant", "designer", "tester"]

# Extraction functions
def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,15}\d', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split("\n")[:10]
    doc = nlp(" ".join(lines))
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_skills(text):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp(skill) for skill in SKILLS_DB]
    matcher.add("SKILLS", patterns)
    doc = nlp(text.lower())
    matches = matcher(doc)
    skills = list(set([doc[start:end].text for _, start, end in matches]))
    return skills

def extract_education(text):
    lines = text.lower().split('\n')
    return [line.strip() for line in lines if any(kw in line for kw in EDUCATION_KEYWORDS)]

def extract_experience(text):
    lines = text.lower().split('\n')
    return [line.strip() for line in lines if any(role in line for role in EXPERIENCE_KEYWORDS)]

def generate_resume_tips(text):
    tips = []
    if "objective" not in text.lower():
        tips.append("[-] Please add your career objective, it will give your career intension to the Recruiters.")
    if "declaration" not in text.lower():
        tips.append("[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you")
    if "hobbies" in text.lower():
        tips.append("[+] Awesome! You have added your Hobbies")
    if "achievement" in text.lower():
        tips.append("[+] Awesome! You have added your Achievements")
    if not tips:
        tips.append("[+] Great! Your resume covers all essential aspects.")
    return "\n".join(tips)

def parse_resume(path):
    text = extract_text_from_pdf(path)
    data = {
        "Filename": os.path.basename(path),
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "Skills": ", ".join(extract_skills(text)),
        "Education": "; ".join(extract_education(text)),
        "Experience": "; ".join(extract_experience(text)),
        "Tips": generate_resume_tips(text)
    }
    return data

# Streamlit UI
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.sidebar.title("📄 Resume Parser")
st.sidebar.markdown("Upload PDF resumes to extract structured data like name, email, skills, education, and experience.")

st.title("📁 Upload Resumes")
uploaded_files = st.file_uploader("Choose PDF resumes", type="pdf", accept_multiple_files=True)

if uploaded_files:
    parsed_results = []

    with st.spinner("🔍 Parsing resumes..."):
        for uploaded_file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name

            try:
                data = parse_resume(temp_path)
                parsed_results.append(data)
            except Exception as e:
                st.error(f"❌ Could not parse {uploaded_file.name}: {str(e)}")

    if parsed_results:
        st.success("✅ Parsing complete!")

        for data in parsed_results:
            st.markdown(f"### 👤 Name: {data['Name'] or 'Not Found'}")
            st.markdown(f"📧 Email: {data['Email'] or 'Not Found'}")
            st.markdown(f"📱 Contact: {data['Phone'] or 'Not Found'}")

            if len(data["Experience"].split(";")) <= 1:
                st.markdown("<h4 style='color: crimson;'>You are at Fresher level!</h4>", unsafe_allow_html=True)
            else:
                st.markdown("<h4 style='color: green;'>You have experience!</h4>", unsafe_allow_html=True)

            if data["Skills"]:
                st.markdown("### 🛠️ Your Current Skills")
                skill_html = ""
                for skill in data["Skills"].split(","):
                    skill_html += f"<span style='background-color:#f44336;color:white;padding:6px 10px;border-radius:20px;margin:4px;display:inline-block'>{skill.strip()} ✘</span>"
                st.markdown(f"<div>{skill_html}</div>", unsafe_allow_html=True)
            else:
                st.warning("No skills found.")

            st.markdown("### 💡 Resume Tips & Ideas")
            for tip in data["Tips"].split("\n"):
                if "Awesome!" in tip:
                    st.markdown(f"<span style='color:green;'>{tip}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:white;'>{tip}</span>", unsafe_allow_html=True)

            st.markdown("---")

        # DataFrame and downloads
        df = pd.DataFrame(parsed_results)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Resumes')
        xlsx_data = output.getvalue()

        st.download_button("⬇️ Download CSV", csv, "parsed_resumes.csv", "text/csv")
        st.download_button("⬇️ Download Excel", xlsx_data, "parsed_resumes.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Please upload one or more PDF files to start.")
