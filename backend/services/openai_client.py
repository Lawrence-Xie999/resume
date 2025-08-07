import openai

from flask import Blueprint, request, jsonify, session
from status import create_status
from services.prompt_engineering import generate_json_from_extracted_texts

apikey_bp=Blueprint("apikey",__name__)

# Get OpenAI API Key
@apikey_bp.route("/service/apikey_bp",methods=["POST"])
def store_apikey():
    status=create_status()
    data=request.get_json()
    if not data:
        status["message"]="store_apikey"
        status["error"]="Data empty"
        status["code"]=400
        return jsonify(status),status["code"]
    
    api_key=data.get("api_key")

    if not api_key or not api_key.startswith("sk-"):
        status["message"]="store_apikey"
        status["error"]="Invalid API Key format"
        status["code"]=401
        return jsonify(status),status["code"]
    
    try:
        openai.api_key=api_key
        openai.models.list()

    except Exception:
        status["message"]="store_apikey"
        status["error"]="Invalid or expired API Key"
        status["code"]=401
        return jsonify(status),status["code"]
    
    session["api_key"]=api_key

    status["message"]="store_apikey: Success"
    status["code"]=200
    
    return jsonify(status),status["code"]

@apikey_bp.route("/service/generate_json",methods=["POST"])
def generate_json():
    status=create_status()
    resume_text=request.form.get("resume_text")
    jd_text=request.form.get("jd_text")
    # if resume_text and jd_text:
    #     status["message"]="Success"
    #     return status
    try:
        status["data"]=generate_json_from_extracted_texts(resume_text,jd_text)
        status["message"]="store_apikey: Success"
        status["code"]=200
        return jsonify(status),status["code"]
    except Exception as e:
        print(str(e))
        return 


