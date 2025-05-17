# app.py

from flask import Flask, render_template
from tools.excel_to_pdf import excel_to_pdf_bp
from tools.pdf_to_excel import pdf_to_excel_bp
from tools.pdf_to_ppt import pdf_to_ppt_bp
from tools.wod_to_pdf import word_to_pdf_bp  # Adjust path
from tools.ppt_to_pdf import ppt_to_pdf_bp  # Adjust path
from flask_cors import CORS
import os
from tools.pdf_to_word import pdf_to_word_bp
# from tools.pdf_to_word import pdf_to_word_bp


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads' 
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure folders exist
import os
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Register Blueprint
app.register_blueprint(excel_to_pdf_bp, url_prefix='/tools')
app.register_blueprint(pdf_to_excel_bp, url_prefix='/tools' )
app.register_blueprint(pdf_to_word_bp, url_prefix='/tools')
app.register_blueprint(word_to_pdf_bp, url_prefix='/tools')
app.register_blueprint(ppt_to_pdf_bp, url_prefix='/tools')
app.register_blueprint(pdf_to_ppt_bp, url_prefix='/tools')
# app.register_blueprint(pdf_to_word_bp, url_prefix='/tools' )

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
