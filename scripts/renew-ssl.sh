#!/bin/bash

# SSL Certificate Renewal Script for VitaChain
# This script renews Let's Encrypt certificates and reloads nginx

set -e

# Configuration
DOMAIN="vitachain.ma"
API_DOMAIN="api.vitachain.ma"
LOG_FILE="/var/log/ssl-renewal.log"

echo "🔄 Starting SSL certificate renewal..." | tee -a $LOG_FILE
echo "📅 $(date)" | tee -a $LOG_FILE

# Function to log and execute
log_exec() {
    echo "🔧 Executing: $*" | tee -a $LOG_FILE
    "$@" | tee -a $LOG_FILE
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ Success: $*" | tee -a $LOG_FILE
    else
        echo "❌ Failed: $* (exit code: $exit_code)" | tee -a $LOG_FILE
    fi
    return $exit_code
}

# Renew certificates
echo "🔐 Renewing SSL certificates..." | tee -a $LOG_FILE

# Renew main domain certificate
if certbot renew --cert-name $DOMAIN --non-interactive --post-hook "docker-compose exec nginx nginx -s reload" 2>&1 | tee -a $LOG_FILE; then
    echo "✅ Certificate for $DOMAIN renewed successfully" | tee -a $LOG_FILE
else
    echo "ℹ️ Certificate for $DOMAIN not due for renewal or renewal failed" | tee -a $LOG_FILE
fi

# Renew API domain certificate
if certbot renew --cert-name $API_DOMAIN --non-interactive --post-hook "docker-compose exec nginx nginx -s reload" 2>&1 | tee -a $LOG_FILE; then
    echo "✅ Certificate for $API_DOMAIN renewed successfully" | tee -a $LOG_FILE
else
    echo "ℹ️ Certificate for $API_DOMAIN not due for renewal or renewal failed" | tee -a $LOG_FILE
fi

# Check certificate expiry
echo "📋 Checking certificate expiry dates..." | tee -a $LOG_FILE

if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    EXPIRY_MAIN=$(openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -enddate | cut -d= -f2)
    echo "📅 $DOMAIN expires: $EXPIRY_MAIN" | tee -a $LOG_FILE
else
    echo "❌ Certificate for $DOMAIN not found" | tee -a $LOG_FILE
fi

if [ -f "/etc/letsencrypt/live/$API_DOMAIN/fullchain.pem" ]; then
    EXPIRY_API=$(openssl x509 -in /etc/letsencrypt/live/$API_DOMAIN/fullchain.pem -noout -enddate | cut -d= -f2)
    echo "📅 $API_DOMAIN expires: $EXPIRY_API" | tee -a $LOG_FILE
else
    echo "❌ Certificate for $API_DOMAIN not found" | tee -a $LOG_FILE
fi

# Test nginx configuration
echo "🧪 Testing nginx configuration..." | tee -a $LOG_FILE
if docker-compose exec -T nginx nginx -t 2>&1 | tee -a $LOG_FILE; then
    echo "✅ Nginx configuration is valid" | tee -a $LOG_FILE
    # Reload nginx gracefully
    echo "🔄 Reloading nginx..." | tee -a $LOG_FILE
    docker-compose exec -T nginx nginx -s reload 2>&1 | tee -a $LOG_FILE
    echo "✅ Nginx reloaded successfully" | tee -a $LOG_FILE
else
    echo "❌ Nginx configuration test failed" | tee -a $LOG_FILE
    exit 1
fi

echo "🎉 SSL renewal process completed!" | tee -a $LOG_FILE
echo "📋 Log saved to: $LOG_FILE" | tee -a $LOG_FILE
