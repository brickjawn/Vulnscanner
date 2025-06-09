#!/bin/bash
# VulnScanner Production Backup Script
# Automated backup of reports, database, and configuration files

set -euo pipefail

# Configuration
BACKUP_DIR="/backup"
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
ENCRYPTION_KEY=${BACKUP_ENCRYPTION_KEY:-"change-this-key"}
BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="vulnscanner_backup_${BACKUP_TIMESTAMP}"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${BACKUP_DIR}/backup.log"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "${BACKUP_DIR}/backup.log" >&2
}

# Create backup directory structure
mkdir -p "${BACKUP_DIR}/reports"
mkdir -p "${BACKUP_DIR}/postgres"
mkdir -p "${BACKUP_DIR}/config"
mkdir -p "${BACKUP_DIR}/archive"

log "Starting backup: ${BACKUP_NAME}"

# Backup reports
if [ -d "/backup/reports" ]; then
    log "Backing up reports..."
    tar -czf "${BACKUP_DIR}/archive/${BACKUP_NAME}_reports.tar.gz" \
        -C /backup/reports . 2>/dev/null || {
        error "Failed to backup reports"
        exit 1
    }
    log "Reports backup completed: ${BACKUP_NAME}_reports.tar.gz"
else
    log "No reports directory found, skipping..."
fi

# Backup PostgreSQL database
if [ -d "/backup/postgres" ]; then
    log "Backing up PostgreSQL database..."
    tar -czf "${BACKUP_DIR}/archive/${BACKUP_NAME}_postgres.tar.gz" \
        -C /backup/postgres . 2>/dev/null || {
        error "Failed to backup PostgreSQL data"
        exit 1
    }
    log "PostgreSQL backup completed: ${BACKUP_NAME}_postgres.tar.gz"
else
    log "No PostgreSQL data directory found, skipping..."
fi

# Backup configuration files
if [ -d "/backup/config" ]; then
    log "Backing up configuration files..."
    tar -czf "${BACKUP_DIR}/archive/${BACKUP_NAME}_config.tar.gz" \
        -C /backup/config . 2>/dev/null || {
        error "Failed to backup configuration files"
        exit 1
    }
    log "Configuration backup completed: ${BACKUP_NAME}_config.tar.gz"
else
    log "No configuration directory found, skipping..."
fi

# Create combined backup archive
log "Creating combined backup archive..."
cd "${BACKUP_DIR}/archive"
tar -czf "${BACKUP_NAME}_combined.tar.gz" \
    "${BACKUP_NAME}"_*.tar.gz 2>/dev/null || {
    error "Failed to create combined backup archive"
    exit 1
}

# Encrypt backup if encryption key is provided
if [ "${ENCRYPTION_KEY}" != "change-this-key" ]; then
    log "Encrypting backup archive..."
    openssl enc -aes-256-cbc -salt -in "${BACKUP_NAME}_combined.tar.gz" \
        -out "${BACKUP_NAME}_combined.tar.gz.enc" \
        -k "${ENCRYPTION_KEY}" || {
        error "Failed to encrypt backup"
        exit 1
    }
    rm "${BACKUP_NAME}_combined.tar.gz"
    log "Backup encrypted: ${BACKUP_NAME}_combined.tar.gz.enc"
fi

# Generate backup manifest
log "Generating backup manifest..."
cat > "${BACKUP_DIR}/archive/${BACKUP_NAME}_manifest.json" << EOF
{
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${BACKUP_TIMESTAMP}",
    "files": [
        $(find "${BACKUP_DIR}/archive" -name "${BACKUP_NAME}*" -type f | \
          sed 's/.*\///' | jq -R . | paste -sd ',')
    ],
    "checksums": {
        $(find "${BACKUP_DIR}/archive" -name "${BACKUP_NAME}*" -type f | \
          while read file; do
              echo "\"$(basename "$file")\": \"$(sha256sum "$file" | cut -d' ' -f1)\","
          done | sed '$ s/,$//')
    },
    "size_bytes": $(find "${BACKUP_DIR}/archive" -name "${BACKUP_NAME}*" -type f -exec du -cb {} + | tail -1 | cut -f1),
    "encrypted": $([ "${ENCRYPTION_KEY}" != "change-this-key" ] && echo "true" || echo "false")
}
EOF

# Cleanup old backups
log "Cleaning up old backups (retention: ${BACKUP_RETENTION_DAYS} days)..."
find "${BACKUP_DIR}/archive" -name "vulnscanner_backup_*" -type f \
    -mtime +${BACKUP_RETENTION_DAYS} -delete || {
    error "Failed to cleanup old backups"
}

# Generate summary
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}/archive/${BACKUP_NAME}"* | head -1 | cut -f1)
TOTAL_FILES=$(find "${BACKUP_DIR}/archive" -name "${BACKUP_NAME}*" -type f | wc -l)

log "Backup completed successfully!"
log "Backup name: ${BACKUP_NAME}"
log "Total size: ${BACKUP_SIZE}"
log "Files created: ${TOTAL_FILES}"
log "Location: ${BACKUP_DIR}/archive/"

# Optional: Send notification (if configured)
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    log "Sending Slack notification..."
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"VulnScanner backup completed: ${BACKUP_NAME} (${BACKUP_SIZE})\"}" \
        "${SLACK_WEBHOOK_URL}" 2>/dev/null || {
        error "Failed to send Slack notification"
    }
fi

if [ -n "${EMAIL_SMTP_SERVER:-}" ]; then
    log "Sending email notification..."
    # Email notification would require additional setup
    # This is a placeholder for email integration
    log "Email notification configured but not implemented"
fi

log "Backup process completed successfully!" 