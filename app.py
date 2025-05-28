import re

# Fallback UI for non-Streamlit environments
USE_STREAMLIT = "False"
try:
    import streamlit as st
    USE_STREAMLIT = "True"
except ImportError:
    print("Streamlit not found. Falling back to console-based interaction.")

# --- Simple Text Extractor ---
def extract_text(file, file_type):
    if file_type == "text/plain":
        return file.read().decode("utf-8")
    elif file_type == "application/pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        return " ".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        import docx
        doc = docx.Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    return ""

# --- Skill Extraction (simple keyword-based) ---
def extract_skills(text):
    skill_keywords = ["python", "java", "aws", "docker", "kubernetes", "sql", "spark", "react", "node", "ci/cd", "jenkins", "linux", "git"]
    text = text.lower()
    found = set(skill for skill in skill_keywords if skill in text)
    return found

# --- Score Calculator ---
def calculate_fit_score(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    if not jd_skills:
        return 0, matched, missing
    score = round((len(matched) / len(jd_skills)) * 100)
    return score, matched, missing

if USE_STREAMLIT:
    st.set_page_config(page_title="AI Resume Matcher", layout="centered")

    st.title("🤖 AI Resume Fit Scorer")
    st.write("Upload a resume and job description to get a Fit Score and Gap Analysis")

    resume_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"])
    jd_file = st.file_uploader("Upload Job Description", type=["txt", "pdf", "docx"])

    if resume_file and jd_file:
        resume_text = extract_text(resume_file, resume_file.type)
        jd_text = extract_text(jd_file, jd_file.type)
        score, matched_skills, missing_skills = calculate_fit_score(resume_text, jd_text)

        st.subheader("✅ Fit Score")
        st.metric(label="Score (out of 100)", value=score)

        st.subheader("🟢 Matching Skills")
        st.write(", ".join(matched_skills) if matched_skills else "None")

        st.subheader("🔴 Missing Skills")
        st.write(", ".join(missing_skills) if missing_skills else "None")

        st.subheader("💡 Recommendation")
        if score >= 80:
            st.success("Great fit! Consider prioritizing this candidate.")
        elif score >= 50:
            st.info("Moderate fit. May require some upskilling or training.")
        else:
            st.warning("Low fit. May not be suitable unless gaps are addressed.")
    else:
        st.info("Please upload both resume and job description to proceed.")

else:
    print("\n=== AI Resume Fit Scorer (Console Mode) ===")
    resume_path = input("Enter path to resume file: ")
    jd_path = input("Enter path to job description file: ")

    import mimetypes
    def get_file_content(path):
        try:
            with open(path, 'rb') as f:
                file_type = mimetypes.guess_type(path)[0] or 'text/plain'
                return extract_text(f, file_type)
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return ""

    resume_text = get_file_content(resume_path)
    jd_text = get_file_content(jd_path)

    score, matched_skills, missing_skills = calculate_fit_score(resume_text, jd_text)
    print(f"\nScore: {score}/100")
    print(f"Matching Skills: {', '.join(matched_skills) if matched_skills else 'None'}")
    print(f"Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}")

    print("\nRecommendation:")
    if score >= 80:
        print("Great fit! Consider prioritizing this candidate.")
    elif score >= 50:
        print("Moderate fit. May require some upskilling or training.")
    else:
        print("Low fit. May not be suitable unless gaps are addressed.")
