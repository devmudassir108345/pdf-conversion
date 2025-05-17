

import os
import uuid
from flask import Blueprint, render_template, request, jsonify, send_file
from flask import current_app as app
from werkzeug.utils import secure_filename
from docx2pdf import convert

word_to_pdf_bp = Blueprint('word_to_pdf', __name__, template_folder='../templates')

# Configuration (used if needed inside the blueprint)
word_to_pdf_bp.upload_folder = 'uploads'
word_to_pdf_bp.output_folder = 'outputs'
word_to_pdf_bp.allowed_extensions = {'doc', 'docx'}

# Ensure folders exist
os.makedirs(word_to_pdf_bp.upload_folder, exist_ok=True)
os.makedirs(word_to_pdf_bp.output_folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in word_to_pdf_bp.allowed_extensions

@word_to_pdf_bp.route('word_to_pdf')
def index():
    return render_template('word_to_pdf.html')  # Create this template

@word_to_pdf_bp.route('word_to_pdf/convert', methods=['POST'])
def convert_word_to_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        unique_id = str(uuid.uuid4())
        word_filename = secure_filename(f"{unique_id}_{file.filename}")
        word_path = os.path.join(word_to_pdf_bp.upload_folder, word_filename)
        file.save(word_path)

        pdf_filename = word_filename.replace('.docx', '.pdf').replace('.doc', '.pdf')
        pdf_path = os.path.join(word_to_pdf_bp.output_folder, pdf_filename)

        try:
            convert(word_path, pdf_path)
            os.remove(word_path)

            return jsonify({
                'success': True,
             'download_url': f'word_to_pdf/download/{pdf_filename}',
                'filename': pdf_filename
            })
        except Exception as e:
            return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file type. Only DOC/DOCX allowed.'}), 400

@word_to_pdf_bp.route('/word_to_pdf/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(word_to_pdf_bp.output_folder, filename)

    if os.path.exists(file_path):
        response = send_file(file_path, as_attachment=True)

        def delete_after_sending():
            try:
                os.remove(file_path)
            except:
                pass

        response.call_on_close(delete_after_sending)
        return response

    return jsonify({'error': 'File not found'}), 404
