#!/bin/bash
# Database Backup Script
# Run this to backup the database

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
MYSQL_CONTAINER="fyp_mysql"
MYSQL_USER="root"
MYSQL_PASSWORD="123456"
DATABASE="db_exam"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting database backup..."
echo "Date: $DATE"

# Backup database
docker exec $MYSQL_CONTAINER mysqldump -u$MYSQL_USER -p$MYSQL_PASSWORD $DATABASE > $BACKUP_DIR/db_exam_$DATE.sql

if [ $? -eq 0 ]; then
    echo "Backup completed successfully!"
    echo "Backup file: $BACKUP_DIR/db_exam_$DATE.sql"
    echo "Size: $(du -h $BACKUP_DIR/db_exam_$DATE.sql | cut -f1)"
else
    echo "Backup failed!"
    exit 1
fi
