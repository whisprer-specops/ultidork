# /etc/nginx/sites-available/prroxy-test.fastping.it.com
server {
    listen 80;
    server_name prroxy-test.fastping.it.com; # Your specific subdomain

    # Optional: Redirect HTTP to HTTPS if you plan to use SSL (highly recommended)
    # return 301 https://$host$request_uri;

    location / {
        proxy_pass http://127.0.0.1:8000; # Gunicorn's address
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # **Crucial for low latency with small responses:**
        # Disable proxy buffering. This means Nginx will send the response
        # from Gunicorn to the client immediately, without buffering it.
        proxy_buffering off;
        # Consider these as well, though proxy_buffering off is the main one for speed
        proxy_request_buffering off;
        proxy_redirect off;
    }

    # If you have any static files (unlikely for a pure ping endpoint, but good practice)
    # location /static/ {
    #     alias /path/to/your/flask_app/static/;
    #     expires 30d; # Cache static files for a long time
    #     add_header Cache-Control "public";
    #     sendfile on; # Optimize static file serving
    # }

    # Enable gzip compression for responses (though for tiny pings, this might add overhead)
    # gzip on;
    # gzip_proxied any;
    # gzip_types text/plain text/xml text/css application/javascript application/json;
    # gzip_comp_level 1; # Lowest compression level for speed
    # gzip_min_length 10; # Only compress if response is at least 10 bytes
}