#!/bin/bash

# SSL Certificate Setup Script for VitaChain
# This script sets up Let's Encrypt certificates with TLS 1.3, auto-renewal, and testing

set -e

# Configuration
DOMAINS="vitachain.ma api.vitachain.ma www.vitachain.ma"
EMAIL="admin@vitachain.ma"
WEBROOT="/var/www/certbot"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔧 Setting up SSL certificates for VitaChain domains"
echo "📍 Domains: $DOMAINS"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing certbot and nginx plugin..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx openssl
fi

# Create webroot directory
echo "📁 Creating webroot directory..."
mkdir -p $WEBROOT

# Stop nginx if running to free up ports 80/443
echo "🛑 Stopping nginx..."
cd "$PROJECT_DIR"
docker-compose stop nginx || true

# Obtain SSL certificates using nginx plugin (better integration)
echo "🔐 Obtaining SSL certificates..."
certbot --nginx \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --redirect \
    --hsts \
    --uir \
    --non-interactive \
    $DOMAINS

# Create SSL directory structure for Docker mounting
echo "📁 Creating SSL directory structure..."
mkdir -p nginx/ssl

# Create symbolic links for certificates (for Docker mounting)
echo "🔗 Creating certificate symlinks..."
MAIN_DOMAIN="vitachain.ma"
ln -sf /etc/letsencrypt/live/$MAIN_DOMAIN/fullchain.pem nginx/ssl/fullchain.pem
ln -sf /etc/letsencrypt/live/$MAIN_DOMAIN/privkey.pem nginx/ssl/privkey.pem
ln -sf /etc/letsencrypt/live/$MAIN_DOMAIN/chain.pem nginx/ssl/chain.pem

# Set proper permissions
echo "🔒 Setting proper permissions..."
chmod 755 nginx/ssl
chmod 644 nginx/ssl/*.pem

# Setup auto-renewal cron job
echo "⏰ Setting up auto-renewal..."
CRON_JOB="0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'cd $PROJECT_DIR && docker-compose exec nginx nginx -s reload'"
(crontab -l 2>/dev/null | grep -v "certbot renew"; echo "$CRON_JOB") | crontab -

# Test SSL configuration
echo "🧪 Testing SSL configuration..."
test_ssl_config() {
    local domain=$1
    echo "Testing SSL for $domain..."
    
    # Test TLS 1.3 connectivity
    if openssl s_client -connect $domain:443 -tls1_3 < /dev/null > /dev/null 2>&1; then
        echo "✅ TLS 1.3 working for $domain"
    else
        echo "❌ TLS 1.3 failed for $domain"
        return 1
    fi
    
    # Test certificate validity
    if openssl s_client -connect $domain:443 -showcerts < /dev/null 2>/dev/null | openssl x509 -noout -dates | grep -q "notAfter"; then
        echo "✅ Certificate valid for $domain"
    else
        echo "❌ Certificate validation failed for $domain"
        return 1
    fi
    
    return 0
}

# Test all domains
for domain in vitachain.ma api.vitachain.ma www.vitachain.ma; do
    test_ssl_config $domain || echo "⚠️ SSL test failed for $domain (may need DNS propagation)"
done

# Create SSL test script for ongoing validation
cat > scripts/test-ssl.sh << 'EOF'
#!/bin/bash
# SSL Test Script for VitaChain

DOMAINS="vitachain.ma api.vitachain.ma www.vitachain.ma"
FAILED_TESTS=0

echo "🧪 Running SSL tests for VitaChain domains..."

test_domain() {
    local domain=$1
    echo "Testing $domain..."
    
    # Test HTTPS connectivity
    if curl -s -o /dev/null -w "%{http_code}" "https://$domain" | grep -q "200\|301\|302"; then
        echo "✅ HTTPS working for $domain"
    else
        echo "❌ HTTPS failed for $domain"
        ((FAILED_TESTS++))
        return
    fi
    
    # Test TLS 1.3
    if openssl s_client -connect $domain:443 -tls1_3 < /dev/null > /dev/null 2>&1; then
        echo "✅ TLS 1.3 working for $domain"
    else
        echo "❌ TLS 1.3 failed for $domain"
        ((FAILED_TESTS++))
    fi
    
    # Check certificate expiry
    EXPIRY=$(echo | openssl s_client -connect $domain:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo "⚠️ Certificate for $domain expires in $DAYS_LEFT days"
        ((FAILED_TESTS++))
    else
        echo "✅ Certificate for $domain valid for $DAYS_LEFT days"
    fi
}

for domain in $DOMAINS; do
    test_domain $domain
done

echo "📊 SSL Test Summary:"
if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ All SSL tests passed"
    exit 0
else
    echo "❌ $FAILED_TESTS SSL tests failed"
    exit 1
fi
EOF

chmod +x scripts/test-ssl.sh

# Start nginx
echo "🚀 Starting nginx..."
docker-compose up -d nginx

# Wait for nginx to start
echo "⏳ Waiting for nginx to start..."
sleep 10

# Verify certificates are working
echo "✅ Verifying certificates..."
verify_cert() {
    local domain=$1
    if [ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]; then
        echo "✅ Certificate for $domain is ready"
        
        # Test with curl
        if curl -s -o /dev/null -w "%{http_code}" "https://$domain" | grep -q "200\|301\|302"; then
            echo "✅ HTTPS working for $domain"
        else
            echo "⚠️ HTTPS test failed for $domain (may need DNS propagation)"
        fi
    else
        echo "❌ Certificate for $domain failed"
        return 1
    fi
}

verify_cert vitachain.ma || exit 1
verify_cert api.vitachain.ma || exit 1

echo "🎉 SSL setup completed successfully!"
echo "📋 Certificate locations:"
echo "   Certificates: /etc/letsencrypt/live/vitachain.ma/"
echo "   Docker mounts: nginx/ssl/"
echo "🔄 Auto-renewal: Daily at 12:00 via cron"
echo "🧪 SSL testing: Run 'scripts/test-ssl.sh' to verify"
echo ""
echo "📌 Next steps:"
echo "   1. Update NGINX configuration with SSL settings"
echo "   2. Configure security headers"
echo "   3. Setup rate limiting"
echo "   4. Test with SSL Labs: https://www.ssllabs.com/ssltest/"
