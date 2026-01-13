#!/bin/bash

# Quick Restore Script for Replit
# Run this AFTER GitHub update to restore your data

echo "🔄 QUICK RESTORE - After GitHub Update"
echo "====================================="

# Find backup directories
BACKUP_DIRS=($(ls -d backup_* 2>/dev/null | sort -r))

if [ ${#BACKUP_DIRS[@]} -eq 0 ]; then
    echo "❌ No backup directories found!"
    echo "💡 Make sure you ran './backup.sh' before the GitHub update"
    exit 1
fi

echo "📁 Found ${#BACKUP_DIRS[@]} backup(s):"
for i in "${!BACKUP_DIRS[@]}"; do
    echo "  $((i+1)). ${BACKUP_DIRS[i]}"
done

# Use newest backup by default
SELECTED_BACKUP="${BACKUP_DIRS[0]}"

if [ ${#BACKUP_DIRS[@]} -gt 1 ]; then
    echo ""
    read -p "Select backup (1-${#BACKUP_DIRS[@]}, or Enter for newest): " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#BACKUP_DIRS[@]} ]; then
        SELECTED_BACKUP="${BACKUP_DIRS[$((choice-1))]}"
    fi
fi

echo ""
echo "🔄 Restoring from: $SELECTED_BACKUP"
echo ""

# Files to restore
FILES=(
    "birthdays.db"
    "user_profiles.json"
    "welcome_data.json"
    "analytics.json"
    "auction_data.json" 
    "deploy_info.json"
)

RESTORED=0

# Restore each file
for file in "${FILES[@]}"; do
    if [ -f "$SELECTED_BACKUP/$file" ]; then
        cp "$SELECTED_BACKUP/$file" .
        SIZE=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "unknown")
        echo "✅ Restored: $file ($SIZE bytes)"
        ((RESTORED++))
    else
        echo "⚠️  Not in backup: $file"
    fi
done

echo ""
echo "📊 RESTORE SUMMARY:"
echo "✅ Files restored: $RESTORED"

# Check if we can verify with the new backup system
if [ -f "backup_manager.py" ]; then
    echo ""
    echo "🔍 Verifying with new backup system..."
    python backup_manager.py stats
    
    echo ""
    echo "💾 Creating first protected backup..."
    python backup_manager.py backup "post_migration"
fi

echo ""
echo "🎉 RESTORE COMPLETE!"
echo "🚀 Next step: python main.py"
echo "🛡️  Your bot now has automatic backup protection!"