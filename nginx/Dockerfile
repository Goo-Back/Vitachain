FROM nginx:alpine

# Remove default NGINX configuration
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copy custom configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Create directories for SSL and logs
RUN mkdir -p /var/www/certbot

# Add healthcheck script
RUN echo '#!/bin/sh\nwget --no-verbose --tries=1 --spider http://localhost/health' > /usr/local/bin/healthcheck.sh && \
    chmod +x /usr/local/bin/healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
