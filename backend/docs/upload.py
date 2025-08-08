import os
import logging

from flask import Blueprint, request, jsonify
from status import create_status

logging.basicConfig(level=logging.INFO)

upload_bp=Blueprint("upload",__name__)

RESUME_UPLOAD_DIRECTORY="uploads/resume"
JD_UPLOAD_DIRECTORY="uploads/jd"
ALLOWED_EXTENSIONS={"pdf","docx","txt"}

# Check file extensions
def allowed_file(filename:str) -> bool:
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# Get a filename different from existing files
def get_unique_filename(folder:str,filename:str)->str:
    name, ext=os.path.splitext(filename)
    counter=1
    new_filename=filename
    while os.path.exists(os.path.join(folder,new_filename)):
        new_filename=f"{name}({counter}){ext}"
        counter+=1
    return new_filename

# Upload file
@upload_bp.route("/upload_resume",methods=["POST"])
def upload_resume():
    status=create_status()
    
    if "file" not in request.files:
        status["message"]="upload_resume"
        status["error"]="No file part"
        status["code"]=400
        return jsonify(status),status["code"]
    
    file=request.files["file"]

    logging.info(f"Uploaded filename: {file.filename}")

    if file.filename=="":
        status["message"]="upload_resume"
        status["error"]="No select file"
        status["code"]=400
        return jsonify(status),status["code"]
    
    print(allowed_file(file.filename))

    if file and allowed_file(file.filename):
        os.makedirs(RESUME_UPLOAD_DIRECTORY, exist_ok=True)
        filename=get_unique_filename(RESUME_UPLOAD_DIRECTORY,file.filename)
        filepath=os.path.join(RESUME_UPLOAD_DIRECTORY,filename)
        file.save(filepath)

        status["message"] = "upload_resume: Success"
        status["data"] = {"filename": filename}
        status["code"] = 200
        return jsonify(status), status["code"]
    
    status["message"] = "upload_resume"
    status["error"] = "Invalid file type"
    status["code"] = 400
    return jsonify(status), status["code"]

@upload_bp.route("/upload_jd", methods=["POST"])
def upload_jd():
    status=create_status()
    
    if "file" not in request.files:
        status["message"]="upload_jd"
        status["error"]="No file part"
        status["code"]=400
        return jsonify(status),status["code"]
    
    file=request.files["file"]

    logging.info(f"Uploaded filename: {file.filename}")

    if file.filename=="":
        status["message"]="upload_jd"
        status["error"]="No select file"
        status["code"]=400
        return jsonify(status),status["code"]
    
    # print(allowed_file(file.filename))

    if file and allowed_file(file.filename):
        os.makedirs(JD_UPLOAD_DIRECTORY, exist_ok=True)
        filename=get_unique_filename(JD_UPLOAD_DIRECTORY,file.filename)
        filepath=os.path.join(JD_UPLOAD_DIRECTORY,filename)
        file.save(filepath)

        status["message"] = "upload_jd: Success"
        status["data"] = {"filename": filename}
        status["code"] = 200
        return jsonify(status), status["code"]
    
    status["message"] = "upload_jd"
    status["error"] = "Invalid file type"
    status["code"] = 400
    return jsonify(status), status["code"]




