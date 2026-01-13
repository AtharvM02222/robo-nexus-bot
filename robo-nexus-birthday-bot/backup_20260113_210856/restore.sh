#!/bin/bash
echo "🔄 RESTORING DATA..."
echo "=================="

# Get the backup directory name (parent of this script)
BACKUP_DIR=$(dirname "$0")

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

for file in "${FILES[@]}"; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        cp "$BACKUP_DIR/$file" .
        echo "✅ Restored: $file"
        ((RESTORED++))
    fi
done

echo ""
echo "📊 RESTORE SUMMARY:"
echo "✅ Files restored: $RESTORED"
echo ""
echo "🚀 Now run: python main.py"
echo "🛡️  Your bot now has automatic backup protection!"
