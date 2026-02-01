#!/bin/bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
nohup /usr/bin/expect deploy_api_gateway_final.exp > deploy_output.log 2>&1 &
echo $! > deploy.pid
echo "Развертывание запущено в фоне, PID: $(cat deploy.pid)"



