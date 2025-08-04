import os
import logging

from flask import Blueprint, request, jsonify
from status import create_status

logging.basicConfig(level=logging.INFO)

upload_bp=Blueprint("upload",__name__)

UPLOAD_FOLDER="uploads"
ALLOWED_EXTENSIONS={"pdf","docx"}

# Check file extensions
def allowed_file(filename:str) -> bool:
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# Get a filename different from existing files
def get_unique_filename(folder,filename):
    name, ext=os.path.splitext(filename)
    counter=1
    new_filename=filename
    while os.path.exists(os.path.join(folder,new_filename)):
        new_filename=f"{name}({counter}){ext}"
        counter+=1
    return new_filename

# Upload file
@upload_bp.route("/upload",methods=["POST"])
def upload_file():
    status=create_status()
    
    if "file" not in request.files:
        status["message"]="upload_file"
        status["error"]="No file part"
        status["code"]=400
        return jsonify(status),status["code"]
    
    file=request.files["file"]

    logging.info(f"Uploaded filename: {file.filename}")

    if file.filename=="":
        status["message"]="upload_file"
        status["error"]="No select file"
        status["code"]=400
        return jsonify(status),status["code"]
    
    print(allowed_file(file.filename))

    if file and allowed_file(file.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename=get_unique_filename(UPLOAD_FOLDER,file.filename)
        filepath=os.path.join(UPLOAD_FOLDER,filename)
        file.save(filepath)

        status["message"] = "File uploaded successfully"
        status["data"] = {"filename": filename}
        status["code"] = 200
        return jsonify(status), status["code"]
    
    status["message"] = "upload_file"
    status["error"] = "Invalid file type"
    status["code"] = 400
    return jsonify(status), status["code"]






