# PDF Merge Service - Remote Version

This version uses a remote Stirling PDF instance (e.g., hosted on Railway) instead of a local Docker container.

## Setup

### Option A: Deploy Stirling PDF to Railway (Recommended for Demo)

### 1. Deploy Stirling PDF to Railway

1. Go to Railway.app
2. Create new project
3. Deploy from Docker image: `frooodle/s-pdf:latest`
4. Set port to `8080` in Railway settings
5. Generate a public domain (e.g., `https://stirling-pdf.up.railway.app`)
6. Note down the API key from Stirling PDF settings

### 2. Import the n8n Workflow

1. Open your n8n instance
2. Import `n8n-pdf-merge-remote.json`
3. Update the workflow:
   - Replace `https://your-stirling-instance.up.railway.app` with your Railway URL
   - Replace `your-api-key-here` with your Stirling PDF API key

### Option B: Run Stirling PDF Locally for Testing

If you want to test locally before deploying:

```bash
cd remote-version
docker-compose up -d
```

Stirling PDF will be available at `http://localhost:8080`

### 3. Test the Workflow

The workflow exposes a webhook endpoint that accepts PDF files and returns the merged result.

**Test with curl:**
```bash
curl -X POST https://your-n8n-instance.com/webhook/pdf-merge \
  -F "file1=@first.pdf" \
  -F "file2=@second.pdf" \
  -o merged.pdf
```

## Differences from Local Version

- **Local version**: Uses file paths and local Stirling PDF Docker container
- **Remote version**: Uses HTTP requests to remote Stirling PDF instance
- **Remote version**: Works with n8n cloud or any n8n instance
- **Remote version**: Webhook-based, can be called from anywhere

## Cost Considerations

- Railway free tier: 500 hours/month (~$5 after that)
- Stirling PDF is memory-intensive (recommend at least 512MB RAM)
- Alternative: Deploy on a VPS (DigitalOcean, Hetzner, etc.) for fixed monthly cost

## Production Recommendations

### Recommended Approach: Deploy on Client's Server

Since the client has a self-hosted n8n instance (`n8n.vo-immobilien.cloud`), the best approach is to deploy Stirling PDF on the same server.

#### Required Access/Credentials:

1. **SSH Access** to the server hosting n8n
   - Hostname/IP address
   - SSH username (typically `root` or a sudo user)
   - SSH private key or password

2. **Docker Access** (verify these are installed on the server):
   - Docker Engine
   - Docker Compose (if n8n is using it)

3. **Server Information Needed**:
   - Current n8n setup (docker-compose or standalone container)
   - Available ports (default: 8080 for Stirling PDF)
   - Docker network name (if using custom networks)

#### Deployment Steps on Client's Server:

**Step 1: Access the Server**
```bash
ssh user@n8n.vo-immobilien.cloud
# or use the server's IP address
```

**Step 2: Check Current Setup**
```bash
# Check if n8n is running with docker-compose
docker-compose ps

# Or check all running containers
docker ps

# Check docker networks
docker network ls
```

**Step 3: Add Stirling PDF to docker-compose.yml**

If using docker-compose, add Stirling PDF service:

```yaml
services:
  n8n:
    # ... existing n8n configuration ...
  
  stirling-pdf:
    image: frooodle/s-pdf:latest
    container_name: stirling-pdf
    ports:
      - "8080:8080"
    environment:
      - DOCKER_ENABLE_SECURITY=false
      - SECURITY_ENABLE_LOGIN=false
    volumes:
      - stirling-data:/usr/share/tessdata
      - stirling-config:/configs
    networks:
      - n8n-network  # Use the same network as n8n
    restart: unless-stopped

volumes:
  stirling-data:
  stirling-config:
```

**Step 4: Deploy**
```bash
docker-compose up -d stirling-pdf
```

**Step 5: Verify**
```bash
# Check if Stirling PDF is running
docker ps | grep stirling

# Test the service
curl http://localhost:8080
```

**Step 6: Update n8n Workflow**

In the n8n workflow, use internal Docker network URL:
- If same Docker network: `http://stirling-pdf:8080`
- If different network: `http://localhost:8080`

#### Alternative: Standalone Docker Container

If not using docker-compose:

```bash
# Create a network (if needed)
docker network create n8n-network

# Run Stirling PDF
docker run -d \
  --name stirling-pdf \
  --network n8n-network \
  -p 8080:8080 \
  -v stirling-data:/usr/share/tessdata \
  -v stirling-config:/configs \
  -e DOCKER_ENABLE_SECURITY=false \
  --restart unless-stopped \
  frooodle/s-pdf:latest

# Connect n8n to the same network (if not already)
docker network connect n8n-network <n8n-container-name>
```

#### Security Considerations:

1. **Firewall**: Ensure port 8080 is NOT exposed publicly (only internal access needed)
2. **API Key**: Configure Stirling PDF with an API key if exposing the port
3. **SSL/TLS**: If accessed externally, set up reverse proxy (nginx/caddy) with SSL
4. **Updates**: Regularly update Stirling PDF: `docker pull frooodle/s-pdf:latest && docker-compose restart stirling-pdf`

#### Benefits of Server Deployment vs Railway:

- ✅ **Zero additional cost** (uses existing server resources)
- ✅ **Faster performance** (no network latency)
- ✅ **More secure** (internal communication only)
- ✅ **Easier maintenance** (same infrastructure)
- ✅ **Better integration** (shared Docker network)
