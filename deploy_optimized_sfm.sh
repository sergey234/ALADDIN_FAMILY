#!/bin/bash

# 🚀 Optimized SFM Deployment Script
# Fast initialization, lazy loading, real SFM data

set -e

echo "🚀 Starting Optimized SFM Deployment..."

# Server details
SERVER="149.154.65.180"
USER="root"
REMOTE_PATH="/opt/aladdin-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run command on server
run_remote() {
    sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@$SERVER "$1"
}

# Function to copy file to server
copy_to_server() {
    sshpass -p 'Sergio675' scp -o StrictHostKeyChecking=no "$1" root@$SERVER:"$REMOTE_PATH/$2"
}

echo -e "${YELLOW}📋 Step 1: Creating backup on server${NC}"
run_remote "cd $REMOTE_PATH && cp -r security security.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null && cp sfm_adapter.py sfm_adapter.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null && cp api_gateway.py api_gateway.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null && echo '✅ Backup created'"

echo -e "${YELLOW}📋 Step 2: Uploading optimized SFM files${NC}"

# Upload optimized SFM singleton
echo "Uploading security/sfm_singleton.py..."
copy_to_server "security/sfm_singleton.py" "security/sfm_singleton.py"

# Upload optimized SFM adapter
echo "Uploading sfm_adapter.py..."
copy_to_server "sfm_adapter.py" "sfm_adapter.py"

# Upload optimized API Gateway
echo "Uploading api_gateway_production_final_complete.py..."
copy_to_server "api_gateway_production_final_complete.py" "api_gateway.py"

echo -e "${YELLOW}📋 Step 3: Syntax check on server${NC}"
run_remote "cd $REMOTE_PATH && python3 -m py_compile security/sfm_singleton.py && python3 -m py_compile sfm_adapter.py && python3 -m py_compile api_gateway.py && echo '✅ All files syntax OK'"

echo -e "${YELLOW}📋 Step 4: Testing SFM initialization${NC}"
run_remote "cd $REMOTE_PATH && python3 -c '
import sys
sys.path.insert(0, \".\")
try:
    from security.sfm_singleton import get_sfm
    import time
    start = time.time()
    sfm = get_sfm()
    init_time = time.time() - start
    print(f\"✅ SFM initialized in {init_time:.3f}s\")
    print(f\"Core functions: {len(sfm._core_functions)}\")
    print(f\"Version: {sfm.version}\")
except Exception as e:
    print(f\"❌ SFM init failed: {e}\")
    exit(1)
'"

echo -e "${YELLOW}📋 Step 5: Testing SFM Adapter${NC}"
run_remote "cd $REMOTE_PATH && timeout 10 python3 -c '
import sys
sys.path.insert(0, \".\")
try:
    from sfm_adapter import sfm_adapter
    import time
    start = time.time()
    health = sfm_adapter.health_check()
    check_time = time.time() - start
    print(f\"✅ Health check in {check_time:.3f}s\")
    print(f\"SFM status: {health.get(\\\"sfm_adapter\\\", \\\"unknown\\\")}\")
    print(f\"Init status: {health.get(\\\"sfm_init_status\\\", \\\"unknown\\\")}\")
    if health.get(\"sfm_adapter\") == \"available\":
        print(\"🎉 SFM is ready!\")
    else:
        print(f\"⏳ SFM status: {health.get(\\\"sfm_init_status\\\", \\\"unknown\\\")}\")
except Exception as e:
    print(f\"❌ Adapter test failed: {e}\")
    exit(1)
'"

echo -e "${YELLOW}📋 Step 6: Restarting API Gateway${NC}"
run_remote "systemctl restart aladdin-main-api-gateway 2>/dev/null || systemctl restart aladdin-api-gateway 2>/dev/null || echo '⚠️ Service restart may have failed'"

echo -e "${YELLOW}📋 Step 7: Waiting for service to start${NC}"
sleep 5

echo -e "${YELLOW}📋 Step 8: Testing API health${NC}"
HEALTH_CHECK=$(run_remote "curl -s http://127.0.0.1:8002/api/health | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    status = data.get(\"sfm_adapter\", \"unknown\")
    init_status = data.get(\"sfm_init_status\", \"unknown\")
    endpoints = data.get(\"endpoints\", 0)
    print(f\"Status: {status}\")
    print(f\"Init: {init_status}\")
    print(f\"Endpoints: {endpoints}\")
    if status == \"available\":
        print(\"SUCCESS\")
    elif status == \"initializing\":
        print(\"INITIALIZING\")
    else:
        print(\"FAILED\")
except:
    print(\"ERROR\")
' 2>/dev/null || echo 'ERROR'")

if echo "$HEALTH_CHECK" | grep -q "SUCCESS"; then
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo -e "${GREEN}SFM is now available with real data!${NC}"
elif echo "$HEALTH_CHECK" | grep -q "INITIALIZING"; then
    echo -e "${YELLOW}⏳ SFM is initializing...${NC}"
    echo -e "${YELLOW}Wait a moment and check again${NC}"
else
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo "Health check output: $HEALTH_CHECK"
    exit 1
fi

echo -e "${YELLOW}📋 Step 9: Testing key endpoints${NC}"
ENDPOINTS_TEST=$(run_remote "curl -s http://127.0.0.1:8002/api/phishing/sensitivity | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    source = data.get(\"source\", \"unknown\")
    print(f\"Phishing endpoint: {source}\")
    if source == \"sfm_real\":
        print(\"SUCCESS\")
    else:
        print(\"FALLBACK\")
except:
    print(\"ERROR\")
' 2>/dev/null || echo 'ERROR'")

if echo "$ENDPOINTS_TEST" | grep -q "SUCCESS"; then
    echo -e "${GREEN}✅ Endpoints returning real SFM data!${NC}"
else
    echo -e "${RED}⚠️ Some endpoints still in fallback mode${NC}"
fi

echo -e "${GREEN}🚀 Optimized SFM deployment completed!${NC}"
echo ""
echo -e "${YELLOW}📱 Mobile app should now receive real SFM data instead of mock!${NC}"