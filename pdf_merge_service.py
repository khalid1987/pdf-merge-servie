from flask import Flask, request, send_file
from PyPDF2 import PdfMerger
import io
import tempfile

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    """Merge multiple PDF files sent as multipart/form-data"""
    files = request.files.getlist('files')
    
    if len(files) < 2:
        return {'error': 'At least 2 PDF files required'}, 400
    
    merger = PdfMerger()
    
    try:
        # Add all PDFs to merger
        for file in files:
            merger.append(file)
        
        # Write merged PDF to bytes
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged.pdf'
        )
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
