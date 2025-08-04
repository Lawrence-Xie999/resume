from flask import Blueprint, request, jsonify, session
from status import create_status

import openai


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

    status["message"]="store_apikey: API Key saved successfully"
    status["code"]=200
    
    return jsonify(status),status["code"]

