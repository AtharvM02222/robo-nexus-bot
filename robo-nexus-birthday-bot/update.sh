#!/bin/bash
# Robo Nexus Bot - Safe Update Script
# This script backs up your data before pulling new code

echo "🔄 Robo Nexus Bot - Safe Update Script"
echo "======================================="

# Create backup directory
mkdir -p backups

# Backup timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo ""
echo "📦 Step 1: Backing up data..."

# Backup database
if [ -f "birthdays.db" ]; then
    cp birthdays.db "backups/birthdays_${TIMESTAMP}.db"
    cp birthdays.db birthdays_backup.db
    echo "   ✅ birthdays.db backed up"
else
    echo "   ⚠️ birthdays.db not found (new installation?)"
fi

# Backup auction data
if [ -f "auction_data.json" ]; then
    cp auction_data.json "backups/auction_data_${TIMESTAMP}.json"
    cp auction_data.json auction_backup.json
    echo "   ✅ auction_data.json backed up"
fi

# Backup analytics
if [ -f "analytics.json" ]; then
    cp analytics.json "backups/analytics_${TIMESTAMP}.json"
    cp analytics.json analytics_backup.json
    echo "   ✅ analytics.json backed up"
fi

# Backup deploy info
if [ -f "deploy_info.json" ]; then
    cp deploy_info.json "backups/deploy_info_${TIMESTAMP}.json"
    cp deploy_info.json deploy_backup.json
    echo "   ✅ deploy_info.json backed up"
fi

echo ""
echo "📥 Step 2: Pulling latest code from GitHub..."
git pull origin main

echo ""
echo "🔄 Step 3: Restoring data..."

# Restore database
if [ -f "birthdays_backup.db" ]; then
    cp birthdays_backup.db birthdays.db
    echo "   ✅ birthdays.db restored"
fi

# Restore auction data
if [ -f "auction_backup.json" ]; then
    cp auction_backup.json auction_data.json
    echo "   ✅ auction_data.json restored"
fi

# Restore analytics
if [ -f "analytics_backup.json" ]; then
    cp analytics_backup.json analytics.json
    echo "   ✅ analytics.json restored"
fi

# Restore deploy info
if [ -f "deploy_backup.json" ]; then
    cp deploy_backup.json deploy_info.json
    echo "   ✅ deploy_info.json restored"
fi

echo ""
echo "✅ Update complete! Your data is safe."
echo ""
echo "🚀 To start the bot, run:"
echo "   python main.py"
echo ""
echo "📁 Backups saved in: ./backups/"
echo "   (Keep last 5 backups, delete older ones manually)"