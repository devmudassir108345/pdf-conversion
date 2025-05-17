from flask import Blueprint, render_template, request, jsonify, send_file, current_app
import os
import uuid
from pdf2docx import Converter
from werkzeug.utils import secure_filename

pdf_to_word_bp = Blueprint('pdf_to_word', __name__, template_folder='../templates')

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

# Page Route
@pdf_to_word_bp.route('pdf-to-word')
def pdf_to_word_page():
    return render_template('pdf_word.html')

# Convert Route
@pdf_to_word_bp.route('pdf-to-word/convert', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        unique_id = str(uuid.uuid4())
        pdf_filename = secure_filename(f"{unique_id}_{file.filename}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        output_folder = current_app.config['OUTPUT_FOLDER']

        pdf_path = os.path.join(upload_folder, pdf_filename)
        file.save(pdf_path)

        docx_filename = pdf_filename.replace('.pdf', '.docx')
        docx_path = os.path.join(output_folder, docx_filename)

        try:
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            os.remove(pdf_path)

            return jsonify({
                'success': True,
                'download_url': f'pdf-to-word/download/{docx_filename}',
                'filename': docx_filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

# Download Route
@pdf_to_word_bp.route('pdf-to-word/download/<filename>', methods=['GET'])
def download_file(filename):
    output_folder = current_app.config['OUTPUT_FOLDER']
    file_path = os.path.join(output_folder, filename)

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
