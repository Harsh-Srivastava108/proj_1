from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    text = ""
    if ext == "pdf":
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    elif ext == "docx":
        text = docx2txt.process(file_path)
    elif ext == "txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    return text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        job_desc = request.form["job_description"]
        uploaded_files = request.files.getlist("resumes")
        results = []

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(path)

                resume_text = extract_text(path)
                docs = [job_desc, resume_text]
                vectorizer = TfidfVectorizer()
                tfidf = vectorizer.fit_transform(docs)
                similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

                results.append((filename, round(similarity * 100, 2)))

        results.sort(key=lambda x: x[1], reverse=True)
        return render_template("index.html", results=results)

    return render_template("index.html", results=[])

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
