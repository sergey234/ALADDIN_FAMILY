server {
    server_name aladdin-ai.ru www.aladdin-ai.ru;

    root /var/www/aladdin-ai.ru;
    index index.html;

    access_log /var/log/nginx/aladdin_ai_access.log;
    error_log  /var/log/nginx/aladdin_ai_error.log;

    location / {
        try_files $uri $uri/ /index.html;
    }

    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/aladdin-ai.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/aladdin-ai.ru/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}
server {
    if ($host = www.aladdin-ai.ru) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = aladdin-ai.ru) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    listen [::]:80;
    server_name aladdin-ai.ru www.aladdin-ai.ru;
    return 404; # managed by Certbot




}