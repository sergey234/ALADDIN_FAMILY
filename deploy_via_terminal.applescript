-- AppleScript для автоматического развертывания через терминал
tell application "Terminal"
    activate
    set currentTab to do script "cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS && echo '🚀 НАЧАЛО РАЗВЕРТЫВАНИЯ' && echo '' && chmod +x deploy_direct.sh && ./deploy_direct.sh"
end tell



