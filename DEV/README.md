# 🧪 **DEV ENVIRONMENT - LOCAL TESTING**

## 📋 **Overview**

Folder ini digunakan untuk pengujian lokal frontend dan backend Shaka Security Scanner dengan AWS Bedrock (profile: sandbox).

---

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# From DEV directory
./setup.sh
```

### **2. Start Backend**
```bash
# Terminal 1
./start-backend.sh
```

### **3. Start Frontend**
```bash
# Terminal 2
./start-frontend.sh
```

### **4. Run Test Scan**
```bash
# Terminal 3
./run-test-scan.sh
```

---

## 📁 **Directory Structure**

```
DEV/
├── README.md                 # This file
├── setup.sh                  # Environment setup script
├── start-backend.sh          # Backend startup script
├── start-frontend.sh         # Frontend startup script
├── run-test-scan.sh          # Test scan script
├── test-config.yaml          # Test configuration
├── backend-logs/             # Backend logs
├── frontend-logs/            # Frontend logs
└── test-results/             # Test scan results
```

---

## ⚙️ **Configuration**

### **Backend Configuration**
- **Port**: 8000
- **AWS Profile**: sandbox
- **AWS Region**: us-east-1
- **AI Model**: Claude 3 Sonnet
- **Rate Limit**: 10 req/sec
- **Log Level**: DEBUG

### **Frontend Configuration**
- **Port**: 3000
- **API Endpoint**: http://localhost:8000
- **Environment**: development
- **Hot Reload**: enabled

---

## 🧪 **Testing Scenarios**

### **Scenario 1: Basic Scan**
- Target: http://testphp.vulnweb.com
- Scanners: Reconnaissance, Vulnerability
- Intensity: Passive
- AI Analysis: Enabled

### **Scenario 2: CMS Scan**
- Target: WordPress demo site
- Scanners: CMS Vulnerability
- Intensity: Active
- AI Analysis: Enabled

### **Scenario 3: Advanced Scan**
- Target: OWASP Juice Shop
- Scanners: Advanced Vulnerability, API
- Intensity: Active
- AI Analysis: Enabled

---

## 📊 **Monitoring**

### **Backend Health Check**
```bash
curl http://localhost:8000/health
```

### **Frontend Health Check**
```bash
curl http://localhost:3000
```

### **View Backend Logs**
```bash
tail -f backend-logs/app.log
```

### **View Frontend Logs**
```bash
tail -f frontend-logs/next.log
```

---

## 🔧 **Troubleshooting**

### **Backend Won't Start**
1. Check Python version: `python3 --version` (need 3.8+)
2. Check dependencies: `pip list | grep shaka`
3. Check AWS credentials: `aws sts get-caller-identity --profile sandbox`
4. Check port availability: `lsof -i :8000`

### **Frontend Won't Start**
1. Check Node version: `node --version` (need 18+)
2. Check dependencies: `cd ../frontend && npm list`
3. Check port availability: `lsof -i :3000`

### **AWS Bedrock Issues**
1. Verify profile: `aws configure list --profile sandbox`
2. Test Bedrock access: `aws bedrock list-foundation-models --profile sandbox --region us-east-1`
3. Check IAM permissions for Bedrock

---

## 📝 **Notes**

- All test data is stored in `test-results/`
- Logs are rotated daily
- Backend runs in development mode with auto-reload
- Frontend runs with hot module replacement
- AWS Bedrock calls are logged for debugging

---

## 🛑 **Cleanup**

```bash
# Stop all services
./stop-all.sh

# Clean logs
rm -rf backend-logs/* frontend-logs/*

# Clean test results
rm -rf test-results/*
```

---

**Created**: April 18, 2026  
**Environment**: Local Development  
**Status**: Ready for Testing
