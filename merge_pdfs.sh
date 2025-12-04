#!/bin/bash

# Stirling PDF Merge Script with API Key
# Usage: ./merge_pdfs.sh file1.pdf file2.pdf output.pdf

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <pdf1> <pdf2> [pdf3...] <output.pdf>"
    exit 1
fi

BASE_URL="http://localhost:8080"
API_KEY="b8659d08-29f1-4436-b079-ffe7a36b5eda"

# Get the last argument (output file)
OUTPUT="${@: -1}"
# Get all but the last argument (input files)
INPUTS="${@:1:$(($#-1))}"

# Build the merge command
echo "Merging PDFs..."
CURL_CMD="curl -X POST -s"
CURL_CMD="$CURL_CMD -H 'X-API-KEY: $API_KEY'"

# Add all input files
for file in $INPUTS; do
    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file"
        exit 1
    fi
    CURL_CMD="$CURL_CMD -F fileInput=@$file"
done

# Execute merge
eval "$CURL_CMD -o $OUTPUT $BASE_URL/api/v1/general/merge-pdfs"

# Check if output file was created and is a PDF
if [ -f "$OUTPUT" ] && file "$OUTPUT" | grep -q "PDF"; then
    echo "Successfully merged PDFs into: $OUTPUT"
    exit 0
else
    echo "Error: Merge failed"
    if [ -f "$OUTPUT" ]; then
        echo "Response:"
        cat "$OUTPUT"
        rm -f "$OUTPUT"
    fi
    exit 1
fi
