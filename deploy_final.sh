#!/bin/bash

# 🚀 FINAL DEPLOYMENT SCRIPT FOR ALADDIN BACKEND
# Syncs local changes to the production server and restarts the service.

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"

echo "=========================================="
echo "🚀 STARTING FINAL DEPLOYMENT"
echo "=========================================="

# 1. Create a backup of the current main.py on the server
echo "💾 Step 1: Backing up main.py on the server..."
expect <<EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "cd $REMOTE_PATH && cp main.py main.py.pre_deploy_$(date +%Y%m%d_%H%M%S)"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        expect {
            eof { }
            timeout { exit 1 }
        }
    }
}
EOF

# 2. Sync files using rsync
echo "📤 Step 2: Syncing files to the server..."
# We sync main.py, app/ directory, security/ directory
# Use expect to provide password to rsync (since it uses ssh)
expect <<EOF
set timeout 300
spawn rsync -avz --progress \
    main.py app/ security/ smart_api_tester.py ALADDIN_JWT_API_ARCHITECTURE_COMPLETE.md \
    $SERVER_USER@$SERVER_IP:$REMOTE_PATH/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        expect {
            eof { }
            timeout { exit 1 }
        }
    }
}
EOF

# 3. Restart the backend services
echo "🔄 Step 3: Restarting backend services..."
expect <<EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "systemctl restart aladdin-main-api-gateway && systemctl restart aladdin-backend"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        expect {
            eof { }
            timeout { exit 1 }
        }
    }
}
EOF

echo "=========================================="
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=========================================="
