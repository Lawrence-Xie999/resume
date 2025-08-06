import docx2txt
import os

from flask import Blueprint, request, jsonify
from status import create_status
from pdfminer.high_level import extract_text


extract_bp=Blueprint("extract",__name__)

def extract_text_from_pdf(file: str) -> str:
    try:
        return extract_text(file)
    except FileNotFoundError as e:
        print(f"File not found: {file}")
        raise

def extract_text_from_docx(file: str) -> str:
    try:
        return docx2txt.process(file)
    except FileNotFoundError as e:
        print(f"File not found: {file}")
        raise

def extract_text_from_txt(file: str) -> str:
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"File not found: {file}")
        raise

@extract_bp.route("/extract_text", methods=["POST"])
def extract_bp()->str:
    status=create_status()
    data=request.get_json
    resume_filename=data.get("resume_filename")
    jd_filename=data.get("jd_filename")

    if not resume_filename or jd_filename:
        status["message"] = "extract_text"
        status["error"] = "No filename provided"
        status["code"] = 400
        return jsonify(status), status["code"]
    
    resume_path=os.path.join("uploads/resume",resume_filename)
    jd_path=os.path.join("uploads/jd",jd_filename)

    if not os.path.exists(resume_path) or os.path.exists(jd_path):
        status["message"] = "extract_text"
        status["error"] = "File does not exist"
        status["code"] = 404
        return jsonify(status), status["code"]
    
    resume_ext=resume_filename.rsplit(".",1)[-1].lower()
    jd_ext=jd_filename.rsplit(".",1)[-1].lower()
    try:
        if resume_ext=="pdf":
            resume_text=extract_text_from_pdf(resume_path)
        elif resume_ext=="docx":
            resume_text=extract_text_from_docx(resume_path)
        elif resume_ext=="txt":
            resume_text=extract_text_from_txt(resume_path)
        else:
            status["message"] = "extract_text"
            status["error"] = "Unsuppoted file type"
            status["code"] = 400
            return jsonify(status), status["code"]
        
        if jd_ext=="pdf":
            jd_text=extract_text_from_pdf(jd_path)
        elif jd_ext=="docx":
            jd_text=extract_text_from_docx(jd_path)
        elif jd_ext=="txt":
            jd_text=extract_text_from_txt(jd_path)
        else:
            status["message"] = "extract_text"
            status["error"] = "Unsuppoted file type"
            status["code"] = 400
            return jsonify(status), status["code"]
        
    except Exception as e:
        status["message"] = "extract_text"
        status["error"] = str(e)
        status["code"] = 500
        return jsonify(status), status["code"]

    status["message"] = "extract_text: Success"
    status["data"] = {"resume_text":resume_text,"jd_text":jd_text}
    status["code"] = 200
    return jsonify(status), status["code"]


