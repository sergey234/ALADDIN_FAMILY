server {
    listen 80;
    listen [::]:80;
    server_name www.aladdin-ai.ru;

    return 301 https://aladdin-ai.ru$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name www.aladdin-ai.ru;

    ssl_certificate /etc/letsencrypt/live/aladdin-ai.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aladdin-ai.ru/privkey.pem;

    return 301 https://aladdin-ai.ru$request_uri;
}
