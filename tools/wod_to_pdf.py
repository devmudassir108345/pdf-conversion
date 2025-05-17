

# import os
# import uuid
# from flask import Blueprint, render_template, request, jsonify, send_file
# from flask import current_app as app
# from werkzeug.utils import secure_filename
# from docx2pdf import convert

# word_to_pdf_bp = Blueprint('word_to_pdf', __name__, template_folder='../templates')

# # Configuration (used if needed inside the blueprint)
# word_to_pdf_bp.upload_folder = 'uploads'
# word_to_pdf_bp.output_folder = 'outputs'
# word_to_pdf_bp.allowed_extensions = {'doc', 'docx'}

# # Ensure folders exist
# os.makedirs(word_to_pdf_bp.upload_folder, exist_ok=True)
# os.makedirs(word_to_pdf_bp.output_folder, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in word_to_pdf_bp.allowed_extensions

# @word_to_pdf_bp.route('word_to_pdf')
# def index():
#     return render_template('word_to_pdf.html')  # Create this template

# @word_to_pdf_bp.route('word_to_pdf/convert', methods=['POST'])
# def convert_word_to_pdf():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     if file and allowed_file(file.filename):
#         unique_id = str(uuid.uuid4())
#         word_filename = secure_filename(f"{unique_id}_{file.filename}")
#         word_path = os.path.join(word_to_pdf_bp.upload_folder, word_filename)
#         file.save(word_path)

#         pdf_filename = word_filename.replace('.docx', '.pdf').replace('.doc', '.pdf')
#         pdf_path = os.path.join(word_to_pdf_bp.output_folder, pdf_filename)

#         try:
#             convert(word_path, pdf_path)
#             os.remove(word_path)

#             return jsonify({
#                 'success': True,
#              'download_url': f'word_to_pdf/download/{pdf_filename}',
#                 'filename': pdf_filename
#             })
#         except Exception as e:
#             return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

#     return jsonify({'error': 'Invalid file type. Only DOC/DOCX allowed.'}), 400

# @word_to_pdf_bp.route('/word_to_pdf/download/<filename>', methods=['GET'])
# def download_file(filename):
#     file_path = os.path.join(word_to_pdf_bp.output_folder, filename)

#     if os.path.exists(file_path):
#         response = send_file(file_path, as_attachment=True)

#         def delete_after_sending():
#             try:
#                 os.remove(file_path)
#             except:
#                 pass

#         response.call_on_close(delete_after_sending)
#         return response

#     return jsonify({'error': 'File not found'}), 404








import os
import tempfile
import shutil
from flask import Blueprint, render_template, request, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
from docx2pdf import convert
import pythoncom

word_to_pdf_bp = Blueprint('word_to_pdf', __name__, template_folder='../templates')

# Configuration
word_to_pdf_bp.upload_folder = 'uploads'
word_to_pdf_bp.output_folder = 'outputs'
word_to_pdf_bp.max_files = 10
word_to_pdf_bp.allowed_extensions = {'doc', 'docx'}

# Ensure folders exist
os.makedirs(word_to_pdf_bp.upload_folder, exist_ok=True)
os.makedirs(word_to_pdf_bp.output_folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in word_to_pdf_bp.allowed_extensions

def clean_filename(filename):
    cleaned = ''.join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).strip()
    return cleaned.replace(' ', '_')

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

@word_to_pdf_bp.route('word_to_pdf', methods=['GET'])
def index():
    clear_directory(word_to_pdf_bp.upload_folder)
    clear_directory(word_to_pdf_bp.output_folder)
    return render_template('word_to_pdf.html')

@word_to_pdf_bp.route('word_to_pdf/convert', methods=['POST'])
def convert_file():
    if 'files[]' not in request.files:
        return jsonify({'success': False, 'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    
    if len(files) > word_to_pdf_bp.max_files:
        return jsonify({
            'success': False,
            'error': f'Maximum {word_to_pdf_bp.max_files} files allowed at once'
        }), 400

    valid_files = []
    invalid_files = []
    
    for file in files:
        if file.filename == '':
            invalid_files.append({'name': file.filename, 'error': 'Empty filename'})
            continue
        
        if not allowed_file(file.filename):
            invalid_files.append({
                'name': file.filename, 
                'error': 'Invalid file type. Only .doc and .docx files are allowed'
            })
            continue
        
        valid_files.append(file)

    if not valid_files:
        return jsonify({
            'success': False,
            'error': 'No valid files to convert',
            'invalid_files': invalid_files
        }), 400

    results = []
    temp_dir = tempfile.mkdtemp()
    
    try:
        pythoncom.CoInitialize()
        
        for file in valid_files:
            try:
                cleaned_name = clean_filename(file.filename)
                secure_name = secure_filename(cleaned_name)
                input_path = os.path.join(temp_dir, secure_name)
                output_filename = os.path.splitext(secure_name)[0] + '.pdf'
                output_path = os.path.join(temp_dir, output_filename)
                
                file.save(input_path)
                convert(input_path, output_path)
                
                final_output_path = os.path.join(word_to_pdf_bp.output_folder, output_filename)
                shutil.move(output_path, final_output_path)
                os.remove(input_path)
                
                results.append({
                    'original_name': file.filename,
                    'pdf_name': output_filename,
                    'download_url': url_for('word_to_pdf.download_file', filename=output_filename),
                    'success': True
                })
                
            except Exception as e:
                results.append({
                    'original_name': file.filename,
                    'success': False,
                    'error': str(e)
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Conversion failed: {str(e)}'
        }), 500
        
    finally:
        pythoncom.CoUninitialize()
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return jsonify({
        'success': True,
        'results': results,
        'invalid_files': invalid_files
    })

@word_to_pdf_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(
            os.path.join(word_to_pdf_bp.output_folder, filename),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'File not found'}), 404

@word_to_pdf_bp.route('/reset', methods=['POST'])
def reset():
    try:
        clear_directory(word_to_pdf_bp.upload_folder)
        clear_directory(word_to_pdf_bp.output_folder)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
