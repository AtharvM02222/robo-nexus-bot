#!/bin/bash

# Simple Backup Script for Replit
# Run this BEFORE updating from GitHub

echo "🔒 SIMPLE BACKUP - Before GitHub Update"
echo "======================================"

# Create backup directory with timestamp
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Created backup directory: $BACKUP_DIR"
echo ""

# List of files to backup
FILES=(
    "birthdays.db"
    "user_profiles.json"
    "welcome_data.json" 
    "analytics.json"
    "auction_data.json"
    "deploy_info.json"
)

BACKED_UP=0
MISSING=0

echo "📦 Backing up files..."

# Backup each file
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        SIZE=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo "unknown")
        echo "✅ Backed up: $file ($SIZE bytes)"
        ((BACKED_UP++))
    else
        echo "⚠️  Not found: $file (normal if feature not used)"
        ((MISSING++))
    fi
done

echo ""
echo "📊 BACKUP SUMMARY:"
echo "✅ Files backed up: $BACKED_UP"
echo "⚠️  Files missing: $MISSING"

# Create restore script
cat > "$BACKUP_DIR/restore.sh" << 'EOF'
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
EOF

chmod +x "$BACKUP_DIR/restore.sh"

# Create simple restore commands file
cat > "$BACKUP_DIR/restore_commands.txt" << EOF
# Simple restore commands (run after GitHub update):

cd $(pwd)
cp $BACKUP_DIR/birthdays.db . 2>/dev/null && echo "✅ Restored birthdays.db"
cp $BACKUP_DIR/user_profiles.json . 2>/dev/null && echo "✅ Restored user_profiles.json"  
cp $BACKUP_DIR/welcome_data.json . 2>/dev/null && echo "✅ Restored welcome_data.json"
cp $BACKUP_DIR/analytics.json . 2>/dev/null && echo "✅ Restored analytics.json"
cp $BACKUP_DIR/auction_data.json . 2>/dev/null && echo "✅ Restored auction_data.json"
cp $BACKUP_DIR/deploy_info.json . 2>/dev/null && echo "✅ Restored deploy_info.json"

# Then start the bot:
python main.py
EOF

echo ""
echo "🎉 BACKUP COMPLETE!"
echo "📁 Backup saved in: $BACKUP_DIR"
echo "📄 Restore script: $BACKUP_DIR/restore.sh"
echo "📄 Manual commands: $BACKUP_DIR/restore_commands.txt"
echo ""
echo "🚀 NEXT STEPS:"
echo "1. ✅ Your data is now backed up"
echo "2. 🔄 Upload new code to GitHub"  
echo "3. 🔄 Update from GitHub in Replit"
echo "4. 🔄 Run: ./$BACKUP_DIR/restore.sh"
echo "5. 🚀 Run: python main.py"
echo ""
echo "🔒 Your data is safe in: $BACKUP_DIR"