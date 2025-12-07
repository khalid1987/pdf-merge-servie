# Quick Reference Card

## 📍 Service Information

**VPS IP**: `[CLIENT_VPS_IP]` ← Update this after deployment

**Service URLs**:
- Stirling PDF: `http://[CLIENT_VPS_IP]:8080`
- Merge Proxy: `http://[CLIENT_VPS_IP]:3000`
- Test UI: `http://[CLIENT_VPS_IP]:8081`

**n8n Integration URL**: `http://[CLIENT_VPS_IP]:3000/merge`

---

## ✅ Quick Health Check

```bash
# SSH to VPS
ssh root@[CLIENT_VPS_IP]

# Check all services
cd /opt/pdf-services && docker compose ps

# Test proxy
curl http://localhost:3000/health
```

**Expected**: All services show "Up" status, health check returns `{"status":"ok"}`

---

## 🔄 Common Commands

### Restart Services
```bash
cd /opt/pdf-services
docker compose restart
```

### View Logs
```bash
docker compose logs -f --tail=50
```

### Check Resource Usage
```bash
docker stats --no-stream
```

### Update Services
```bash
docker compose pull
docker compose up -d
```

---

## 🧪 Test Merge Functionality

### Using Web UI (Easiest)
1. Open browser: `http://[CLIENT_VPS_IP]:8081`
2. Drag & drop 2 PDFs
3. Click "Merge PDFs"
4. Download result

### Using Command Line
```bash
curl -X POST "http://localhost:3000/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"data": "'$(base64 -w 0 test1.pdf)'", "filename": "test1.pdf"},
      {"data": "'$(base64 -w 0 test2.pdf)'", "filename": "test2.pdf"}
    ]
  }' | jq -r '.success'
```

**Expected**: `true`

---

## 🚨 Emergency Procedures

### Services Not Responding
```bash
cd /opt/pdf-services
docker compose restart
docker compose logs
```

### Out of Memory
```bash
docker compose down
docker system prune -f
docker compose up -d
```

### Check Disk Space
```bash
df -h
docker system df
```

---

## 📊 n8n Workflow Integration

**After `extract_binary_files` node, add**:

1. **IF** - Check both PDFs exist
2. **Code** - Prepare for Merge Service *(see DEPLOYMENT_GUIDE.md)*
3. **HTTP Request** - `POST http://[CLIENT_VPS_IP]:3000/merge`
4. **Code** - Convert to Binary *(see DEPLOYMENT_GUIDE.md)*

**Full workflow code**: See `n8n-test-proxy-merge.json` for working example

---

## 📞 Support

**Deployment Team**: [Your Contact Info]

**When contacting support, provide**:
- Error message
- Output of: `docker compose logs --tail=100`
- What you were trying to do

---

## 📚 Full Documentation

- **CLIENT_SUMMARY.md** - Overview for management
- **DEPLOYMENT_GUIDE.md** - Complete deployment steps
- **MAINTENANCE_GUIDE.md** - Detailed troubleshooting
- **README.md** - Project overview

---

## 🔐 Security Notes

- Proxy service on port 3000 should only be accessible from n8n server
- Web UI on port 8081 can be public (optional, for testing)
- Keep services updated monthly: `docker compose pull && docker compose up -d`

---

## ⚡ Performance Tips

- **Normal**: Merge 2 PDFs in 2-5 seconds
- **Slow** (>10s): Check `docker stats` - may need more RAM
- **Failing**: Check logs for specific error

---

**Last Updated**: [Date]  
**Deployed By**: [Your Name]  
**Version**: 1.0

