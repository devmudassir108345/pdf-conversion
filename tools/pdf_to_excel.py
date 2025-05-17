import os
import traceback
from flask import Blueprint, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import pdfplumber
import pandas as pd
from datetime import datetime

pdf_to_excel_bp = Blueprint('pdf_to_excel', __name__, template_folder='../templates')

# Configuration
pdf_to_excel_bp.upload_folder = 'uploads'
pdf_to_excel_bp.output_folder = 'outputs'
pdf_to_excel_bp.allowed_extensions = {'pdf'}

os.makedirs(pdf_to_excel_bp.upload_folder, exist_ok=True)
os.makedirs(pdf_to_excel_bp.output_folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in pdf_to_excel_bp.allowed_extensions

def convert_pdf_to_excel(pdf_path, excel_path):
    try:
        all_tables = []
        text_data = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if table:
                                cleaned_table = []
                                for row in table:
                                    cleaned_row = [str(cell).strip() if cell else '' for cell in row]
                                    if any(cell != '' for cell in cleaned_row):
                                        cleaned_table.append(cleaned_row)
                                if cleaned_table:
                                    all_tables.extend(cleaned_table)
                except Exception as e:
                    print(f"[ERROR] Error extracting tables: {e}")
                    continue

            if not all_tables:
                for page in pdf.pages:
                    try:
                        text = page.extract_text()
                        if text:
                            lines = text.split('\n')
                            for line in lines:
                                if line.strip():
                                    text_data.append([line.strip()])
                    except Exception as e:
                        print(f"[ERROR] Error extracting text: {e}")
                        continue

        data_to_export = all_tables if all_tables else text_data

        if not data_to_export:
            print("[ERROR] No data found in PDF")
            return False

        df = pd.DataFrame(data_to_export)

        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, header=False)
            worksheet = writer.sheets['Sheet1']
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).str.len().max(), len(str(col)))
                worksheet.set_column(i, i, min(max_len + 2, 50))

        return True

    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}\n{traceback.format_exc()}")
        return False

@pdf_to_excel_bp.route('/pdf_to_excel')
def index():
    return render_template('pdf_to_excel.html')

@pdf_to_excel_bp.route('/pdf_to_excel/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400

    try:
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(pdf_to_excel_bp.upload_folder, filename)
        file.save(pdf_path)

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            return jsonify({'error': 'Uploaded file is empty or invalid'}), 400

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        excel_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.xlsx"
        excel_path = os.path.join(pdf_to_excel_bp.output_folder, excel_filename)

        if convert_pdf_to_excel(pdf_path, excel_path):
            try:
                os.remove(pdf_path)
            except:
                pass

            return jsonify({
                'success': True,
                'download_url': f'pdf_to_excel/download/{excel_filename}',
                'filename': excel_filename
            })
        else:
            try:
                os.remove(pdf_path)
            except:
                pass
            return jsonify({
                'error': 'Conversion failed. The PDF might be scanned (image-based) or contain no extractable data.',
                'details': 'Try using an OCR tool first if your PDF is scanned.'
            }), 400

    except Exception as e:
        print(f"[ERROR] Exception in convert route: {e}\n{traceback.format_exc()}")
        try:
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
            if 'excel_path' in locals() and os.path.exists(excel_path):
                os.remove(excel_path)
        except:
            pass

        return jsonify({
            'error': 'An unexpected error occurred during conversion',
            'details': str(e)
        }), 500

@pdf_to_excel_bp.route('/pdf_to_excel/download/<filename>')
def download(filename):
    try:
        excel_path = os.path.join(pdf_to_excel_bp.output_folder, filename)

        if not os.path.exists(excel_path) or os.path.getsize(excel_path) == 0:
            return jsonify({'error': 'File not found or is empty'}), 404

        return send_file(
            excel_path,
            download_name=filename,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"[ERROR] Download failed: {e}\n{traceback.format_exc()}")
        return jsonify({'error': 'File download failed'}), 500
