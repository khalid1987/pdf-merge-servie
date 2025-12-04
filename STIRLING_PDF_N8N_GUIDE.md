# Stirling PDF with n8n Integration Guide

## Docker Setup

### Pull the Docker Image
```bash
docker pull frooodle/s-pdf
```

### Run Stirling PDF Container
```bash
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/stirling-data:/usr/share/tessdata \
  -e SECURITY_ENABLELOGIN=true \
  -e SECURITY_INITIALLOGIN_USERNAME=admin \
  -e SECURITY_INITIALLOGIN_PASSWORD=einstein87 \
  --name stirling-pdf \
  frooodle/s-pdf
```

### Useful Docker Commands
```bash
# Check if container is running
docker ps | grep stirling

# Stop the container
docker stop stirling-pdf

# Start existing container
docker start stirling-pdf

# Remove container (to recreate)
docker rm -f stirling-pdf

# View logs
docker logs stirling-pdf
```

## API Authentication

### Your API Key
```
b8659d08-29f1-4436-b079-ffe7a36b5eda
```

### How to Get API Key
1. Login to Stirling PDF at `http://localhost:8080`
2. Click the gear icon (⚙️) in top-right corner
3. Go to Account Settings
4. Find your API key in the account details

## n8n HTTP Request Node Configuration

### For Merging PDFs from n8n Docker Container

**URL**: `http://172.18.0.1:8080/api/v1/general/merge-pdfs`
> Note: Use `172.18.0.1` (Docker gateway IP) instead of `localhost` when calling from n8n container

**Method**: `POST`

**Authentication**: None

**Headers**:
| Name | Value |
|------|-------|
| X-API-KEY | b8659d08-29f1-4436-b079-ffe7a36b5eda |

**Send Body**: Yes

**Body Content Type**: Form-Data Multipart

**Specify Body**: Using Fields Below

**Body Parameters**:
- **Parameter Type**: n8n Binary File
- **Name**: `fileInput`
- **Input Binary Field**: `data`

**Options**:
- **Batching** → **Batch Size**: `0` (to process all items together)
- **Response** → **Response Format**: File

## Complete n8n Workflow Example

### Workflow: Merge Multiple PDFs

1. **Read Binary Files** node
   - File(s) to Read: `/path/to/first.pdf, /path/to/second.pdf`
   - Property Name: `data`

2. **HTTP Request** node (configured as above)
   - This receives all PDF items and merges them

3. **Write Binary File** node (optional)
   - File Name: `/tmp/merged_output.pdf`
   - Property Name: `data`

## Command Line Testing

### Using curl (from host machine)
```bash
curl -X POST "http://localhost:8080/api/v1/general/merge-pdfs" \
  -H "X-API-KEY: b8659d08-29f1-4436-b079-ffe7a36b5eda" \
  -F "fileInput=@first.pdf" \
  -F "fileInput=@second.pdf" \
  -o merged.pdf
```

### Using the Bash Script
```bash
./merge_pdfs.sh first.pdf second.pdf output.pdf
```

### Using the Python Script
```bash
python3 merge_pdfs.py first.pdf second.pdf -o output.pdf
```

## Troubleshooting

### n8n Cannot Connect to Stirling PDF

**Error**: `ECONNREFUSED` or `ENOTFOUND`

**Solution**: Use Docker gateway IP instead of localhost
- From n8n container: `http://172.18.0.1:8080`
- From host machine: `http://localhost:8080`

### Invalid Request Content (400 Error)

**Possible causes**:
1. Missing or incorrect `X-API-KEY` header
2. Binary data not being sent correctly
3. Wrong `fileInput` parameter name
4. Not sending multiple items together (check Batch Size = 0)

### Authentication Required Error

**Solution**: Make sure your API key is included in the header:
```
X-API-KEY: b8659d08-29f1-4436-b079-ffe7a36b5eda
```

## API Documentation

- **Local Swagger UI**: http://localhost:8080/swagger-ui/index.html
- **Online Documentation**: https://docs.stirlingpdf.com/API
- **Swagger Hub**: https://app.swaggerhub.com/apis-docs/Frooodle/Stirling-PDF/

## Other Useful Endpoints

All endpoints require the `X-API-KEY` header.

### Add Watermark
```bash
curl -X POST "http://localhost:8080/api/v1/general/add-watermark" \
  -H "X-API-KEY: b8659d08-29f1-4436-b079-ffe7a36b5eda" \
  -F "fileInput=@input.pdf" \
  -F "watermarkType=text" \
  -F "watermarkText=CONFIDENTIAL" \
  -F "fontSize=30" \
  -F "opacity=0.5"
```

### Split PDF
```bash
curl -X POST "http://localhost:8080/api/v1/general/split-pages" \
  -H "X-API-KEY: b8659d08-29f1-4436-b079-ffe7a36b5eda" \
  -F "fileInput=@input.pdf" \
  -F "pages=1,3,5-7"
```

### Compress PDF
```bash
curl -X POST "http://localhost:8080/api/v1/general/compress-pdf" \
  -H "X-API-KEY: b8659d08-29f1-4436-b079-ffe7a36b5eda" \
  -F "fileInput=@input.pdf" \
  -F "optimizeLevel=2"
```

## Environment Variables

Set these when starting the container:

```bash
docker run -d \
  -p 8080:8080 \
  -e SECURITY_ENABLELOGIN=true \
  -e SECURITY_INITIALLOGIN_USERNAME=admin \
  -e SECURITY_INITIALLOGIN_PASSWORD=einstein87 \
  -e SECURITY_CUSTOMGLOBALAPIKEY=your-global-api-key \
  --name stirling-pdf \
  frooodle/s-pdf
```

**Common Environment Variables**:
- `SECURITY_ENABLELOGIN`: Enable/disable login (true/false)
- `SECURITY_INITIALLOGIN_USERNAME`: Initial admin username
- `SECURITY_INITIALLOGIN_PASSWORD`: Initial admin password
- `SECURITY_CUSTOMGLOBALAPIKEY`: Set a global API key
