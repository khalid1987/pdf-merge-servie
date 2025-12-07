# PDF Merge Service - Stirling PDF Integration

This project provides multiple ways to merge PDF files using the Stirling PDF API:

1. **Flask Microservice** - Deployable API service for PDF merging
2. **n8n Workflow** - Automation workflow for self-hosted n8n
3. **Standalone Scripts** - Python and Bash scripts for direct API usage

## Components

### Flask Service (`pdf_merge_service.py`)
A simple Flask API that accepts PDF files and returns a merged PDF.

**Deployment:**
```bash
docker build -f Dockerfile.pdfmerge -t pdf-merge-service .
docker run -p 5000:5000 pdf-merge-service
```

**Usage:**
```bash
curl -X POST http://localhost:5000/merge \
  -F "files=@first.pdf" \
  -F "files=@second.pdf" \
  -o merged.pdf
```

### n8n Workflow (`n8n-pdf-merge-test.json`)
Import this workflow into n8n to merge PDFs automatically.

**Requirements:**
- Self-hosted n8n with curl installed (see `Dockerfile.n8n` in n8n-setup folder)
- Stirling PDF running on Docker network

### Standalone Scripts
- **`merge_pdfs.py`** - Python script using requests library
- **`merge_pdfs.sh`** - Bash script using curl

## Stirling PDF Setup

### Docker Compose
```yaml
services:
  stirling-pdf:
    image: frooodle/s-pdf
    ports:
      - "8080:8080"
    environment:
      - SECURITY_ENABLE_LOGIN=true
      - SECURITY_INITIALLOGIN_USERNAME=admin
      - SECURITY_INITIALLOGIN_PASSWORD=einstein87
```

### API Authentication
Set up an API key in Stirling PDF:
1. Log in to Stirling PDF (http://localhost:8080)
2. Go to Account Settings → API Keys
3. Generate a new API key
4. Use the key in `X-API-KEY` header

## Documentation

See `STIRLING_PDF_N8N_GUIDE.md` for comprehensive documentation including:
- Detailed API usage examples
- Troubleshooting guide
- Docker networking setup
- n8n integration patterns

## Deployment Options

### Free Hosting (for testing/demos)
- **Render.com** - Recommended, free tier with 750 hours/month
- **Railway.app** - $5 free credit monthly
- **Fly.io** - Free tier with limits

### Production
- VPS (Digital Ocean, Linode, etc.)
- Docker deployment recommended

## Environment Variables

For Flask service:
```bash
STIRLING_PDF_URL=http://172.18.0.1:8080  # Docker gateway IP
STIRLING_API_KEY=your-api-key-here
```

## License

MIT
