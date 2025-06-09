# VulnScanner Production Deployment Guide

## 🚀 Production Deployment Checklist

### Pre-Deployment Security Checklist

- [ ] **Environment Configuration**
  - [ ] Copy `config/production.env` to `.env` and customize
  - [ ] Generate secure API keys and passwords
  - [ ] Configure encryption keys for backups
  - [ ] Set up proper file permissions (no root user)

- [ ] **Network Security**
  - [ ] Configure firewall rules
  - [ ] Set up SSL certificates for HTTPS
  - [ ] Configure VPN access if needed
  - [ ] Whitelist IP addresses if applicable

- [ ] **Database Security**
  - [ ] Use strong PostgreSQL passwords
  - [ ] Enable database encryption at rest
  - [ ] Configure database backups
  - [ ] Set up database connection limits

- [ ] **Container Security**
  - [ ] Scan container images for vulnerabilities
  - [ ] Use non-root users in containers
  - [ ] Enable security policies (seccomp, AppArmor)
  - [ ] Configure resource limits

## 📋 Deployment Steps

### 1. Infrastructure Setup

```bash
# Create production directories
sudo mkdir -p /opt/vulnscanner/{reports,logs,config}
sudo chown -R 1000:1000 /opt/vulnscanner

# Set proper permissions
sudo chmod 755 /opt/vulnscanner
sudo chmod 750 /opt/vulnscanner/{reports,logs}
sudo chmod 640 /opt/vulnscanner/config
```

### 2. Configuration

```bash
# Copy and customize environment file
cp config/production.env .env
nano .env

# Generate secure passwords
openssl rand -base64 32  # For API keys
openssl rand -base64 24  # For database passwords
```

### 3. SSL Certificate Setup

```bash
# Create SSL directory
mkdir -p config/nginx/ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout config/nginx/ssl/server.key \
  -out config/nginx/ssl/server.crt

# Or use Let's Encrypt for production
certbot certonly --standalone -d your-domain.com
```

### 4. Deploy Production Stack

```bash
# Build and deploy production services
docker-compose -f docker-compose.prod.yml up -d

# Verify all services are healthy
docker-compose -f docker-compose.prod.yml ps
```

### 5. Initial Setup

```bash
# Initialize database schema
docker-compose -f docker-compose.prod.yml exec vulnscanner \
  python scripts/init_db.py

# Create admin user
docker-compose -f docker-compose.prod.yml exec vulnscanner \
  python scripts/create_admin.py

# Run initial health check
docker-compose -f docker-compose.prod.yml exec vulnscanner \
  python monitoring/health_check.py
```

## 📊 Monitoring Setup

### Prometheus Configuration

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'vulnscanner'
    static_configs:
      - targets: ['vulnscanner:9090']
    scrape_interval: 30s
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

### Grafana Dashboards

Access Grafana at `http://your-server:3000` with admin/admin123 (change default password).

Key dashboards to import:
- System metrics (CPU, Memory, Disk)
- Application metrics (scan performance, error rates)
- Security alerts (failed authentications, unusual activity)

### Log Aggregation

Configure ELK stack for centralized logging:

```yaml
# monitoring/filebeat/filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/vulnscanner/*.log
  fields:
    service: vulnscanner
  fields_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "vulnscanner-logs-%{+yyyy.MM.dd}"
```

## 🔐 Security Hardening

### 1. System Security

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install security updates
sudo unattended-upgrades

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### 2. Docker Security

```bash
# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1

# Scan images for vulnerabilities
docker scan vulnscanner:latest

# Use Docker secrets for sensitive data
echo "my-secret-password" | docker secret create db_password -
```

### 3. Network Security

```bash
# Configure iptables firewall
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP

# Save firewall rules
sudo iptables-save > /etc/iptables/rules.v4
```

### 4. SSL/TLS Configuration

Configure Nginx with strong SSL settings:

```nginx
# config/nginx/nginx.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
```

## 📈 Performance Optimization

### 1. Resource Allocation

```yaml
# Adjust container resources based on usage
deploy:
  resources:
    limits:
      memory: 4G      # Increase for large scans
      cpus: '8.0'     # Scale with concurrent scans
    reservations:
      memory: 1G
      cpus: '2.0'
```

### 2. Database Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET effective_cache_size = '3GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
SELECT pg_reload_conf();
```

### 3. Caching Strategy

```bash
# Configure Redis for caching
# Set appropriate memory limits and eviction policies
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🔄 Backup and Recovery

### Automated Backup

```bash
# Set up daily backups via cron
echo "0 2 * * * docker-compose -f /opt/vulnscanner/docker-compose.prod.yml run --rm backup-service" | crontab -
```

### Recovery Procedures

```bash
# Restore from backup
BACKUP_FILE="/backup/archive/vulnscanner_backup_20231201_020000_combined.tar.gz.enc"

# Decrypt backup (if encrypted)
openssl enc -aes-256-cbc -d -in "$BACKUP_FILE" -out restored_backup.tar.gz -k "encryption-key"

# Extract and restore
tar -xzf restored_backup.tar.gz
# Follow specific restore procedures for each component
```

## 📋 Operational Procedures

### Health Monitoring

```bash
# Check system health
docker-compose -f docker-compose.prod.yml exec vulnscanner python monitoring/health_check.py

# View service logs
docker-compose -f docker-compose.prod.yml logs -f vulnscanner

# Monitor resource usage
docker stats
```

### Scaling Procedures

```bash
# Scale scanner instances
docker-compose -f docker-compose.prod.yml up -d --scale vulnscanner=3

# Load balancer configuration required for multiple instances
```

### Security Incident Response

1. **Immediate Response**
   - Isolate affected systems
   - Preserve logs and evidence
   - Notify security team

2. **Investigation**
   - Analyze logs in Kibana
   - Check system metrics in Grafana
   - Review audit trails

3. **Recovery**
   - Apply security patches
   - Update configurations
   - Restore from clean backups if needed

### Maintenance Windows

```bash
# Planned maintenance procedure
# 1. Notify users
# 2. Stop non-critical services
docker-compose -f docker-compose.prod.yml stop vulnscanner-gui

# 3. Perform updates
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. Restart services
docker-compose -f docker-compose.prod.yml up -d
```

## 🚨 Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs vulnscanner
   
   # Check resource limits
   docker system df
   free -h
   ```

2. **Database connection issues**
   ```bash
   # Verify database health
   docker-compose -f docker-compose.prod.yml exec postgres pg_isready
   
   # Check connection string
   docker-compose -f docker-compose.prod.yml exec vulnscanner env | grep DATABASE
   ```

3. **Performance issues**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Check system metrics
   htop
   iotop
   ```

### Emergency Contacts

- **Security Team**: security@yourcompany.com
- **Infrastructure Team**: infrastructure@yourcompany.com
- **On-call Engineer**: +1-XXX-XXX-XXXX

## 📚 Additional Resources

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Container Security](https://owasp.org/www-project-docker-security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html) 