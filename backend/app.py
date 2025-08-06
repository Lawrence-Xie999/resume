import os

from flask import Flask
from services.openai_client import apikey_bp
from dotenv import load_dotenv
from docs.upload import upload_bp

load_dotenv()

app=Flask(__name__)
app.secret_key=os.getenv("SESSION_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SESSION_SECRET_KEY Not Set")


app.register_blueprint(apikey_bp)
app.register_blueprint(upload_bp)

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5001, debug= True)

# http://127.0.0.1:5001


