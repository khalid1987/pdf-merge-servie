# Maintenance & Troubleshooting Guide

## 🔍 Daily Operations

### Check Service Health

```bash
# Quick health check
docker compose ps

# Expected output:
# NAME              STATUS    PORTS
# stirling-pdf      Up        0.0.0.0:8080->8080/tcp
# pdf-merge-proxy   Up        0.0.0.0:3000->3000/tcp
```

### View Recent Activity

```bash
# Last 50 log lines
docker compose logs --tail=50

# Follow live logs
docker compose logs -f

# Specific service
docker compose logs -f pdf-merge-proxy
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Proxy Returns 500 Error

**Symptom**: n8n workflow fails, proxy logs show error

```bash
# Check proxy logs
docker compose logs pdf-merge-proxy | tail -20
```

**Common Causes**:
1. **Invalid base64 data**
   - Check n8n Code node is extracting binary.data properly
   - Verify: `console.log('File 1 length:', files[0].data.length)`

2. **Stirling PDF not responding**
   ```bash
   # Test Stirling directly
   docker exec pdf-merge-proxy ping stirling-pdf
   
   # Check Stirling health
   curl http://localhost:8080/api/v1/info
   ```

3. **Out of memory**
   ```bash
   # Check memory usage
   docker stats --no-stream
   
   # Increase memory limit (edit docker-compose.yml)
   services:
     stirling-pdf:
       deploy:
         resources:
           limits:
             memory: 2G
   ```

**Solution**:
```bash
# Restart services
docker compose restart

# If persists, check full logs
docker compose logs stirling-pdf | grep -i error
```

---

### Issue 2: "source.on is not a function" in n8n

**Symptom**: n8n HTTP Request node fails with this error

**Cause**: Trying to send binary data directly in bodyParameters

**Solution**: Use the proxy pattern (already implemented)
- Ensure Code node converts binary.data to base64
- Send as JSON to proxy (not binary)
- Proxy handles multipart conversion

---

### Issue 3: Merged PDF is Corrupted

**Symptom**: Download succeeds but PDF won't open

**Debugging**:
```bash
# Test proxy with known-good PDFs
curl -X POST "http://localhost:3000/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"data": "'$(base64 -w 0 /path/to/test1.pdf)'", "filename": "test1.pdf"},
      {"data": "'$(base64 -w 0 /path/to/test2.pdf)'", "filename": "test2.pdf"}
    ]
  }' | jq -r '.data' | base64 -d > merged.pdf

# Try to open merged.pdf
```

**Possible Causes**:
1. **Base64 encoding issue in n8n**
   - Ensure Code node uses: `item.binary.pdf.data` (not stringified)

2. **Truncated response**
   - Check n8n response size limits
   - Large PDFs may need chunked handling

3. **Stirling PDF issue**
   ```bash
   # Update Stirling to latest
   docker compose pull stirling-pdf
   docker compose up -d stirling-pdf
   ```

---

### Issue 4: Services Won't Start After Reboot

**Symptom**: VPS rebooted, services not running

```bash
# Check why services stopped
docker compose ps -a

# Restart
cd /opt/pdf-services
docker compose up -d

# Check logs for startup errors
docker compose logs
```

**Prevention**: Services already have `restart: unless-stopped` policy

If still not starting:
```bash
# Check disk space
df -h

# Check Docker service
systemctl status docker

# Restart Docker if needed
systemctl restart docker
docker compose up -d
```

---

### Issue 5: Slow Merge Performance

**Symptom**: Takes >30 seconds to merge 2 PDFs

**Debugging**:
```bash
# Check CPU/Memory
docker stats

# Check if Stirling is swapping
free -h
```

**Solutions**:
1. **Increase VPS resources**
   - Minimum 2GB RAM recommended
   - 2 CPU cores for optimal performance

2. **Reduce concurrent requests**
   - n8n workflow: Set max concurrent executions to 1-2

3. **Check PDF size**
   ```javascript
   // In n8n Prepare node, log file sizes
   console.log('Invoice size:', item.binary.invoice.data.length);
   console.log('Supplement size:', item.binary.supplement.data.length);
   ```

---

## 🔧 Maintenance Tasks

### Weekly: Check Disk Space

```bash
# Check overall disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up if needed (removes stopped containers, unused images)
docker system prune -a --volumes
```

### Monthly: Update Services

```bash
cd /opt/pdf-services

# Backup current state
docker compose down
tar -czf backup-$(date +%Y%m%d).tar.gz docker-compose.yml pdf-proxy/

# Pull latest images
docker compose pull

# Recreate containers
docker compose up -d

# Verify
docker compose ps
curl http://localhost:3000/health
```

### As Needed: View Logs

```bash
# Real-time monitoring
docker compose logs -f

# Search for errors
docker compose logs | grep -i error

# Export logs for analysis
docker compose logs --since 24h > logs-$(date +%Y%m%d).txt
```

---

## 📊 Monitoring

### Health Check Endpoints

```bash
# Proxy health
curl http://localhost:3000/health
# Returns: {"status":"ok","service":"pdf-merge-proxy"}

# Stirling info
curl http://localhost:8080/api/v1/info
# Returns: {"version":"...", "modules": [...]}
```

### Performance Metrics

```bash
# Container resource usage
docker stats --no-stream

# Disk usage
docker system df
```

### Log Analysis

```bash
# Count successful merges today
docker compose logs pdf-merge-proxy --since 24h | grep "PDF merge successful" | wc -l

# Find errors
docker compose logs --since 24h | grep -E "ERROR|WARN"

# Average response time (if added to logs)
docker compose logs pdf-merge-proxy --since 1h | grep "Response time" | awk '{sum+=$NF; count++} END {print sum/count}'
```

---

## 🛡️ Security Maintenance

### Check for Updates

```bash
# Check current versions
docker exec stirling-pdf cat /app/version.txt
docker exec pdf-merge-proxy node --version

# Update Docker images
docker compose pull
docker compose up -d
```

### Review Access Logs

```bash
# Who's accessing the proxy?
docker compose logs pdf-merge-proxy | grep POST | awk '{print $1}' | sort | uniq -c

# Suspicious activity?
docker compose logs | grep -E "400|401|403|500"
```

### Firewall Rules

```bash
# Verify firewall status
ufw status numbered

# If exposed to internet, restrict proxy access
ufw delete allow 3000/tcp
ufw allow from N8N_SERVER_IP to any port 3000
```

---

## 💾 Backup Strategy

### What to Backup

1. **Configuration files**
   - `/opt/pdf-services/docker-compose.yml`
   - `/opt/pdf-services/pdf-proxy/`

2. **Docker volumes** (if you store configs)
   ```bash
   docker run --rm -v pdf-services_stirling_configs:/data -v $(pwd):/backup \
     alpine tar czf /backup/volumes-backup.tar.gz /data
   ```

### Backup Script

Create `/opt/pdf-services/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configs
cd /opt/pdf-services
tar -czf $BACKUP_DIR/pdf-services-$DATE.tar.gz \
  docker-compose.yml \
  pdf-proxy/

# Keep last 7 days
find $BACKUP_DIR -name "pdf-services-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/pdf-services-$DATE.tar.gz"
```

```bash
# Make executable
chmod +x /opt/pdf-services/backup.sh

# Add to cron (daily at 2am)
crontab -e
# Add line:
0 2 * * * /opt/pdf-services/backup.sh >> /var/log/pdf-backup.log 2>&1
```

---

## 🔄 Recovery Procedures

### Restore from Backup

```bash
# Stop services
cd /opt/pdf-services
docker compose down

# Extract backup
tar -xzf /opt/backups/pdf-services-YYYYMMDD_HHMMSS.tar.gz

# Start services
docker compose up -d

# Verify
docker compose ps
curl http://localhost:3000/health
```

### Rebuild from Scratch

If configuration is lost:

```bash
# Stop and remove everything
docker compose down -v

# Re-deploy using DEPLOYMENT_GUIDE.md
# Files should still be in /opt/pdf-services/pdf-proxy/

# Start fresh
docker compose up -d
```

---

## 📈 Performance Tuning

### Optimize Docker

```bash
# Edit /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Restart Docker
systemctl restart docker
docker compose up -d
```

### Optimize Stirling PDF

Edit `docker-compose.yml`:

```yaml
services:
  stirling-pdf:
    environment:
      - JAVA_TOOL_OPTIONS=-Xmx1024m  # Limit Java memory
      - DOCKER_ENABLE_SECURITY=false
      - INSTALL_BOOK_AND_ADVANCED_HTML_OPS=false  # Disable unused features
```

---

## 🆘 Emergency Contacts

### When to Escalate

Contact deployment team if:
- Services down for >15 minutes
- Memory consistently >90%
- Disk space <10% free
- Repeated merge failures (>5 in 1 hour)
- Security alerts/suspicious activity

### Quick Fix Commands

```bash
# Service not responding
docker compose restart

# Out of memory
docker compose down
docker system prune -f
docker compose up -d

# Complete reset (last resort)
docker compose down -v
docker system prune -af
# Then redeploy using DEPLOYMENT_GUIDE.md
```

---

## 📚 Additional Resources

- **Stirling PDF Docs**: https://github.com/Stirling-Tools/Stirling-PDF
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **n8n Documentation**: https://docs.n8n.io/

---

**Questions?** Contact the deployment team with:
- Error messages (from `docker compose logs`)
- What you were trying to do
- What happened instead
- Steps you've already tried

