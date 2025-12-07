# Production Deployment Guide

## 📦 What to Deploy

This guide walks you through deploying the PDF merge service to the client's VPS.

---

## 🎯 Pre-requisites

### Client VPS Requirements
- **OS**: Linux (Ubuntu/Debian preferred)
- **RAM**: Minimum 2GB
- **Disk**: 10GB free space
- **Access**: SSH root or sudo access
- **Docker**: Installed (we'll install if needed)

### What You'll Need
- Client VPS IP address
- SSH credentials
- Client's n8n instance URL

---

## 📋 Deployment Steps

### Step 1: Prepare Deployment Files

On your local machine, create a deployment package:

```bash
cd /home/khalid/Desktop/Pro/pdf-merge-service-temp

# Create deployment archive
tar -czf pdf-merge-production.tar.gz \
  proxy-service/ \
  test-ui/index.html \
  DEPLOYMENT_GUIDE.md \
  MAINTENANCE_GUIDE.md
```

### Step 2: Access Client VPS

```bash
# Replace with client's VPS IP
ssh root@CLIENT_VPS_IP
```

### Step 3: Install Docker (if not installed)

```bash
# Check if Docker is installed
docker --version

# If not installed:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify installation
docker --version
docker compose version
```

### Step 4: Create Working Directory

```bash
# Create directory structure
mkdir -p /opt/pdf-services
cd /opt/pdf-services
```

### Step 5: Copy Files from Test VPS

From your **local machine**:

```bash
# Copy from test VPS to local
scp -r khalid@95.216.205.234:~/pdf-proxy ./pdf-proxy-backup

# Copy to client VPS
scp -r ./pdf-proxy-backup root@CLIENT_VPS_IP:/opt/pdf-services/pdf-proxy
```

Or directly from test VPS to client VPS:

```bash
ssh khalid@95.216.205.234 "cd ~/pdf-proxy && tar -czf - ." | \
  ssh root@CLIENT_VPS_IP "cd /opt/pdf-services && mkdir -p pdf-proxy && cd pdf-proxy && tar -xzf -"
```

### Step 6: Deploy Stirling PDF

On **client VPS**:

```bash
cd /opt/pdf-services

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  stirling-pdf:
    image: frooodle/s-pdf:latest
    container_name: stirling-pdf
    ports:
      - "8080:8080"
    volumes:
      - stirling_data:/usr/share/tessdata
      - stirling_configs:/configs
    environment:
      - DOCKER_ENABLE_SECURITY=false
      - INSTALL_BOOK_AND_ADVANCED_HTML_OPS=false
      - LANGS=de_DE,en_US
    restart: unless-stopped
    networks:
      - pdf_network

  pdf-merge-proxy:
    build: ./pdf-proxy
    container_name: pdf-merge-proxy
    ports:
      - "3000:3000"
    depends_on:
      - stirling-pdf
    restart: unless-stopped
    networks:
      - pdf_network

volumes:
  stirling_data:
  stirling_configs:

networks:
  pdf_network:
    driver: bridge
EOF

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f
```

### Step 7: Verify Services

```bash
# Test Stirling PDF
curl http://localhost:8080/api/v1/info

# Test Proxy
curl http://localhost:3000/health
```

Expected responses:
- Stirling: JSON with version info
- Proxy: `{"status":"ok","service":"pdf-merge-proxy"}`

### Step 8: Deploy Test Web UI (Optional)

```bash
# Copy test UI file
cd /opt/pdf-services
mkdir -p test-ui
# Copy index.html from your local machine
```

```bash
# On local machine
scp test-ui/index.html root@CLIENT_VPS_IP:/opt/pdf-services/test-ui/
```

```bash
# Back on client VPS
docker run -d \
  --name pdf-test-ui \
  -p 8081:80 \
  -v /opt/pdf-services/test-ui/index.html:/usr/share/nginx/html/index.html:ro \
  --restart unless-stopped \
  nginx:alpine
```

### Step 9: Configure Firewall (if applicable)

```bash
# Allow necessary ports
ufw allow 8080/tcp  # Stirling PDF
ufw allow 3000/tcp  # Proxy
ufw allow 8081/tcp  # Test UI (optional)
ufw status
```

### Step 10: Test End-to-End

From your **local machine**:

```bash
# Test with real PDFs
curl -X POST "http://CLIENT_VPS_IP:3000/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"data": "'$(base64 -w 0 test1.pdf)'", "filename": "test1.pdf"},
      {"data": "'$(base64 -w 0 test2.pdf)'", "filename": "test2.pdf"}
    ]
  }' | jq '.success'

# Should return: true
```

---

## 🔧 Configure n8n Workflow

### Files to Update

The client needs to add 3 nodes after `extract_binary_files`:

1. **IF Node: "Check Both PDFs Exist"**
   ```
   Condition: 
   - invoice_binary_found = true AND
   - supplement_binary_found = true
   ```

2. **Code Node: "Prepare for Merge Service"**
   ```javascript
   const item = $input.item;
   const files = [
     {
       data: item.binary.invoice.data,
       filename: item.json.invoice_name || 'invoice.pdf'
     },
     {
       data: item.binary.supplement.data,
       filename: item.json.supplement_name || 'supplement.pdf'
     }
   ];
   
   return { json: { files } };
   ```

3. **HTTP Request: "Call Merge Service"**
   ```
   Method: POST
   URL: http://CLIENT_VPS_IP:3000/merge
   Content Type: JSON
   Body: 
     - Parameter: files
     - Value: ={{ $json.files }}
   ```

4. **Code Node: "Convert Merged PDF to Binary"**
   ```javascript
   const response = $input.item.json;
   
   if (!response.success) {
     throw new Error(`Merge failed: ${response.error}`);
   }
   
   return {
     json: {
       success: response.success,
       filename: response.filename,
       size: response.size
     },
     binary: {
       data: {
         data: response.data,
         mimeType: response.mimeType,
         fileName: response.filename
       }
     }
   };
   ```

### Update URLs in Test Workflows

Replace all instances of `95.216.205.234` with `CLIENT_VPS_IP`:
- In n8n workflows
- In test UI (if deployed)
- In documentation

---

## 📊 Service URLs

After deployment, services will be available at:

- **Stirling PDF**: `http://CLIENT_VPS_IP:8080`
- **Merge Proxy**: `http://CLIENT_VPS_IP:3000`
- **Test UI**: `http://CLIENT_VPS_IP:8081` (if deployed)

---

## 🔒 Security Considerations

### Production Recommendations

1. **Use HTTPS** (via reverse proxy like nginx)
2. **Restrict access** to proxy service:
   ```bash
   # Only allow n8n server IP
   ufw allow from N8N_SERVER_IP to any port 3000
   ```
3. **Enable Stirling PDF authentication** (edit docker-compose.yml):
   ```yaml
   environment:
     - DOCKER_ENABLE_SECURITY=true
     - SECURITY_ENABLE_LOGIN=true
   ```

4. **Regular updates**:
   ```bash
   docker compose pull
   docker compose up -d
   ```

---

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose logs stirling-pdf
docker compose logs pdf-merge-proxy

# Check container status
docker compose ps

# Restart services
docker compose restart
```

### Proxy Can't Reach Stirling

```bash
# Test from inside proxy container
docker exec pdf-merge-proxy ping stirling-pdf

# Check network
docker network ls
docker network inspect pdf-services_pdf_network
```

### Memory Issues

```bash
# Check resource usage
docker stats

# Increase if needed (edit docker-compose.yml)
services:
  stirling-pdf:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📦 Backup & Recovery

### Backup Configuration

```bash
# Create backup
cd /opt/pdf-services
tar -czf backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  pdf-proxy/

# Store backup safely
scp backup-*.tar.gz user@backup-server:/backups/
```

### Restore

```bash
# Extract backup
cd /opt/pdf-services
tar -xzf backup-YYYYMMDD.tar.gz

# Restart services
docker compose up -d
```

---

## 📝 Maintenance Commands

### View Logs
```bash
docker compose logs -f --tail=100
```

### Restart Services
```bash
docker compose restart
```

### Update Services
```bash
docker compose pull
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### Full Cleanup (careful!)
```bash
docker compose down -v  # Removes volumes too
```

---

## ✅ Deployment Checklist

- [ ] Docker installed on client VPS
- [ ] Files copied from test VPS
- [ ] docker-compose.yml created
- [ ] Services started (`docker compose up -d`)
- [ ] Services verified (curl tests)
- [ ] Firewall configured
- [ ] n8n workflow updated with client VPS IP
- [ ] End-to-end test successful
- [ ] Client informed of service URLs
- [ ] Documentation provided

---

## 📞 Support Information

After deployment, provide client with:
- Service URLs
- How to access test UI
- How to check service status
- Your contact for support

**Deployment Complete!** ✅

