import json
import os

from flask import Flask, render_template, Blueprint, request, current_app
from weasyprint import HTML, CSS
from status import create_status
from docs.upload import get_unique_filename

generate_bp=Blueprint("generate",__name__)

@generate_bp.route("/generate", methods=["POST"])  
def generate_pdf():
    status = create_status()  
    
    html_template = request.json.get("html_template")  
    json_file = request.json.get("json_file")
    
    if not html_template or not json_file:  
        status["message"] = "generate_pdf"
        status["error"] = "No template or json file"
        status["code"] = 400
        return status
    
    try:
        with current_app.app_context():  
            with open(json_file) as f:
                data = json.load(f)
            
            rendered_template = render_template(html_template, **data)
            export_path = get_unique_filename("export", "generated_resume")
            HTML(string=rendered_template).write_pdf(export_path)
            
            status["message"] = "generate_pdf: Success"
            status["code"] = 200
            status["data"] = {"export_path":export_path}  
            
    except Exception as e:
        status["message"] = "generate_pdf"
        status["error"] = f"PDF generate failed: {str(e)}"
        status["code"] = 401
        print(str(e))
        return status

    status["message"]="generate_pdf:Success"
    status["code"]=200
    return status


