server {
    listen 443 ssl; # Listen on HTTPS port
    server_name prroxy-test.fastping.it.com;

    ssl_certificate /etc/nginx/ssl/cloudflare_origin.pem; # Path to your Cloudflare origin certificate
    ssl_certificate_key /etc/nginx/ssl/cloudflare_origin.key; # Path to your Cloudflare origin key

    # Minimal TLS setup for speed and security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256';

    location / {
        proxy_pass http://127.0.0.1:12345; # Your Gunicorn port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off; # Crucial for low latency
        proxy_request_buffering off;
        proxy_redirect off;
    }
}