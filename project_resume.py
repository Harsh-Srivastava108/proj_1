import spacy
import re
import pdfplumber
import pandas as pd
import os
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

# Skill keywords
SKILLS_DB = ["python", "java", "c++", "sql", "javascript", "html", "css",
             "machine learning", "deep learning", "nlp", "data analysis", "excel", "communication"]

EDUCATION_KEYWORDS = ["bachelor", "master", "b.sc", "m.sc", "b.tech", "m.tech", "ph.d", "mba", "bca", "mca"]
EXPERIENCE_KEYWORDS = ["intern", "developer", "engineer", "manager", "analyst", "consultant", "designer", "tester"]

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

def parse_resume(path):
    text = extract_text_from_pdf(path)
    data = {
        "Filename": os.path.basename(path),
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "Skills": ", ".join(extract_skills(text)),
        "Education": "; ".join(extract_education(text)),
        "Experience": "; ".join(extract_experience(text))
    }
    return data

# 🔁 Batch processing
def process_directory(folder_path):
    results = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            full_path = os.path.join(folder_path, file)
            print(f"Parsing: {file}")
            data = parse_resume(full_path)
            results.append(data)

    df = pd.DataFrame(results)
    df.to_csv("all_resumes.csv", index=False)
    df.to_excel("all_resumes.xlsx", index=False)
    print("✅ Exported to all_resumes.csv and all_resumes.xlsx")

# 👉 Set folder path containing PDFs
pdf_folder = "resume"  # Replace with your folder name
process_directory(pdf_folder)
