#!/usr/bin/env python3
import requests
import sys
from pathlib import Path

API_KEY = "b8659d08-29f1-4436-b079-ffe7a36b5eda"
BASE_URL = "http://localhost:8080"

def merge_pdfs(pdf_files, output_file):
    """Merge multiple PDF files using Stirling PDF API"""
    files = []
    try:
        for pdf_file in pdf_files:
            if not Path(pdf_file).exists():
                raise FileNotFoundError(f"File not found: {pdf_file}")
            files.append(('fileInput', (Path(pdf_file).name, open(pdf_file, 'rb'), 'application/pdf')))
        
        headers = {'X-API-KEY': API_KEY}
        
        response = requests.post(
            f"{BASE_URL}/api/v1/general/merge-pdfs",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"Successfully merged {len(pdf_files)} PDFs into {output_file}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    finally:
        for _, file_tuple in files:
            file_tuple[1].close()

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 merge_pdfs.py <pdf1> <pdf2> [pdf3...] -o <output.pdf>")
        sys.exit(1)
    
    try:
        output_index = sys.argv.index('-o')
        input_files = sys.argv[1:output_index]
        output_file = sys.argv[output_index + 1]
    except (ValueError, IndexError):
        print("Error: Please specify output file with -o flag")
        sys.exit(1)
    
    if len(input_files) < 2:
        print("Error: At least 2 PDF files required")
        sys.exit(1)
    
    try:
        success = merge_pdfs(input_files, output_file)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
