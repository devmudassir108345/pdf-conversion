

import os
from flask import Blueprint, render_template, request, send_file, jsonify, current_app
from werkzeug.utils import secure_filename
import pandas as pd
from fpdf import FPDF
from datetime import datetime

excel_to_pdf_bp = Blueprint('excel_to_pdf', __name__ , template_folder='../templates')
# PDF Class
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Excel to PDF Conversion', 0, 1, 'C')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Allowed file check
def allowed_file(filename):
    allowed = {'xlsx', 'xls', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

# Excel to PDF conversion logic
def convert_excel_to_pdf(excel_path, pdf_path):
    try:
        if excel_path.endswith('.csv'):
            df = pd.read_csv(excel_path)
        else:
            df = pd.read_excel(excel_path, engine='openpyxl')
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 10)

        col_widths = []
        for col in df.columns:
            max_len = max(df[col].astype(str).str.len().max(), len(str(col)))
            col_widths.append(min(max_len * 2, 60))

        pdf.set_fill_color(200, 220, 255)
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], 10, str(col), border=1, fill=True)
        pdf.ln()

        fill = False
        for _, row in df.iterrows():
            for i, item in enumerate(row):
                pdf.cell(col_widths[i], 10, str(item), border=1, fill=fill)
            pdf.ln()
            fill = not fill

        pdf.output(pdf_path)
        return True
    except Exception as e:
        print(f"[ERROR] Excel conversion failed: {e}")
        return False

# Routes

@excel_to_pdf_bp.route('excel_to_pdf')
def index():
    return render_template('excel_to_pdf.html')  # show the form

@excel_to_pdf_bp.route('/excel-to-pdf/convert', methods=['POST'])
def convert():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    output_folder = current_app.config['OUTPUT_FOLDER']

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            excel_path = os.path.join(upload_folder, filename)
            file.save(excel_path)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            pdf_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.pdf"
            pdf_path = os.path.join(output_folder, pdf_filename)

            if convert_excel_to_pdf(excel_path, pdf_path):
                return jsonify({
                    'success': True,
                    'download_url': f'excel-to-pdf/download/{pdf_filename}',
                    'filename': pdf_filename
                })
            else:
                return jsonify({'error': 'Conversion failed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type (XLSX, XLS, CSV only)'}), 400

@excel_to_pdf_bp.route('excel-to-pdf/download/<filename>')
def download(filename):
    try:
        return send_file(
            os.path.join(current_app.config['OUTPUT_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
