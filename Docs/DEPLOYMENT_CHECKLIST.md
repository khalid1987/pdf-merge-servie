# Pre-Deployment Checklist

## 📋 Before Client Approval

- [ ] Client reviewed **CLIENT_SUMMARY.md**
- [ ] Client approved proxy solution approach
- [ ] Client confirmed VPS access details
- [ ] Client confirmed n8n instance URL
- [ ] Budget/timeline approved

---

## 🎯 Client Information Collection

**Collect from client**:
- [ ] VPS IP address: `___________________`
- [ ] SSH credentials (user/password or key)
- [ ] n8n instance URL: `___________________`
- [ ] Preferred deployment date/time
- [ ] Technical contact for coordination

---

## 🔧 Pre-Deployment Preparation

### On Your Local Machine

- [ ] Test VPS (95.216.205.234) is still running
- [ ] Verify all test services work:
  - [ ] Stirling PDF: http://95.216.205.234:8080
  - [ ] Proxy: http://95.216.205.234:3000/health
  - [ ] Test UI: http://95.216.205.234:8081
  - [ ] n8n test workflow: n8n-test-proxy-merge.json

- [ ] Create deployment package:
  ```bash
  cd /home/khalid/Desktop/Pro/pdf-merge-service-temp
  tar -czf deployment-package.tar.gz \
    proxy-service/ \
    test-ui/ \
    CLIENT_SUMMARY.md \
    DEPLOYMENT_GUIDE.md \
    MAINTENANCE_GUIDE.md \
    QUICK_REFERENCE.md \
    n8n-test-proxy-merge.json \
    docker-compose-production.yml
  ```

- [ ] Backup test VPS configurations:
  ```bash
  ssh khalid@95.216.205.234 "cd ~/pdf-proxy && tar -czf ~/pdf-proxy-backup.tar.gz ."
  scp khalid@95.216.205.234:~/pdf-proxy-backup.tar.gz ./backups/
  ```

### Documentation Updates

- [ ] Update **QUICK_REFERENCE.md** with client VPS IP
- [ ] Update **DEPLOYMENT_GUIDE.md** examples with client VPS IP
- [ ] Prepare n8n workflow JSON with updated URLs
- [ ] Create handover document with access credentials (secure)

---

## 🚀 Deployment Day Checklist

### Phase 1: VPS Setup (30 minutes)

- [ ] SSH access to client VPS confirmed
- [ ] Docker installed and verified: `docker --version`
- [ ] Directory created: `/opt/pdf-services`
- [ ] Firewall configured (ports 8080, 3000, 8081)

### Phase 2: File Transfer (15 minutes)

- [ ] proxy-service/ directory copied
- [ ] docker-compose.yml created
- [ ] test-ui/index.html copied (if needed)
- [ ] Permissions set correctly: `chown -R root:root /opt/pdf-services`

### Phase 3: Service Deployment (20 minutes)

- [ ] Stirling PDF container started
- [ ] Proxy service built and started
- [ ] Test UI deployed (optional)
- [ ] All containers show "Up" status: `docker compose ps`

### Phase 4: Verification (15 minutes)

- [ ] Stirling PDF accessible: `curl http://localhost:8080/api/v1/info`
- [ ] Proxy health check passes: `curl http://localhost:3000/health`
- [ ] Test UI loads (if deployed): `http://CLIENT_VPS_IP:8081`
- [ ] End-to-end test with real PDFs successful

### Phase 5: n8n Integration (30 minutes)

- [ ] Backup existing Rechnungspostfach workflow
- [ ] Import test workflow (n8n-test-proxy-merge.json)
- [ ] Update URLs to client VPS IP
- [ ] Test workflow with sample PDFs
- [ ] Integrate into main workflow:
  - [ ] Add IF node after extract_binary_files
  - [ ] Add Prepare for Proxy Code node
  - [ ] Add HTTP Request to merge service
  - [ ] Add Convert to Binary Code node
  - [ ] Test with real email attachments

### Phase 6: Documentation Handover (15 minutes)

- [ ] Provide client with service URLs
- [ ] Share **QUICK_REFERENCE.md**
- [ ] Share **MAINTENANCE_GUIDE.md**
- [ ] Demo test UI (if deployed)
- [ ] Show how to check service status
- [ ] Provide support contact information

---

## ✅ Post-Deployment Verification

### Immediate (same day)

- [ ] Monitor logs for first hour: `docker compose logs -f`
- [ ] Watch for any errors or warnings
- [ ] Verify resource usage acceptable: `docker stats`
- [ ] Test merge functionality 3-5 times
- [ ] Confirm n8n workflow executes successfully

### Day 2-7

- [ ] Check service status daily
- [ ] Monitor for any failures in n8n workflow
- [ ] Review logs for errors: `docker compose logs | grep -i error`
- [ ] Verify disk space not filling: `df -h`
- [ ] Collect performance metrics (merge times)

### Week 2

- [ ] Schedule check-in with client
- [ ] Review any issues encountered
- [ ] Verify backup strategy in place
- [ ] Confirm client comfortable with maintenance tasks
- [ ] Plan for monthly update schedule

---

## 🛡️ Rollback Plan

**If deployment fails**:

1. **Immediate**: Stop services
   ```bash
   docker compose down
   ```

2. **Option A**: Revert to test VPS
   - Update n8n workflow URLs back to 95.216.205.234
   - Continue using test VPS temporarily

3. **Option B**: Redeploy from scratch
   - Review logs to identify issue
   - Fix configuration
   - Restart deployment process

4. **Communicate**: Inform client of:
   - What went wrong
   - Current status (using test VPS)
   - New deployment timeline
   - What will be different

---

## 📊 Success Criteria

**Deployment is successful when**:

- [ ] All 3 services running on client VPS
- [ ] Health checks pass
- [ ] Test merge completes in <10 seconds
- [ ] n8n workflow executes without errors
- [ ] Real email attachments merge successfully
- [ ] Client can access test UI (if deployed)
- [ ] Client confirms satisfaction
- [ ] Documentation provided
- [ ] Support handover complete

---

## 🆘 Emergency Contacts

**During Deployment**:
- Your phone: `___________________`
- Client technical contact: `___________________`
- Backup support: `___________________`

**Issue Escalation**:
- Can't SSH to VPS → Client IT team
- Docker issues → Check MAINTENANCE_GUIDE.md
- n8n workflow fails → Review n8n logs
- Proxy errors → Check proxy logs: `docker compose logs pdf-merge-proxy`

---

## 📝 Notes Section

**Pre-Deployment Meeting Notes**:
```
Date: ___________________
Attendees: ___________________
Decisions: ___________________
Concerns: ___________________
```

**Deployment Day Notes**:
```
Start Time: ___________________
Completion Time: ___________________
Issues Encountered: ___________________
Solutions Applied: ___________________
```

**Post-Deployment Notes**:
```
Client Feedback: ___________________
Performance Observations: ___________________
Follow-up Items: ___________________
```

---

## 🎓 Handover Checklist

**Provide to Client**:
- [ ] All service URLs (written down)
- [ ] QUICK_REFERENCE.md (printed or PDF)
- [ ] MAINTENANCE_GUIDE.md
- [ ] Access credentials (if created any)
- [ ] Support contact information
- [ ] Backup schedule recommendation
- [ ] Monthly update procedure

**Provide to Client's Technical Team**:
- [ ] DEPLOYMENT_GUIDE.md
- [ ] docker-compose.yml with comments
- [ ] Proxy source code (pdf-proxy/)
- [ ] n8n workflow JSON files
- [ ] SSH access details (if managing)
- [ ] Monitoring/alerting recommendations

---

**Checklist Version**: 1.0  
**Created**: [Date]  
**Deployment Engineer**: [Your Name]  
**Client**: [Client Name]

