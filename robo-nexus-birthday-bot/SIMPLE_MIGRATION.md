# 🚀 Super Simple Migration (Using cp commands)

## The Problem
You need to upload new code to GitHub, but it will wipe your current data **once**.

## ✅ Super Simple Solution

### Step 1: Backup (Before GitHub Upload)
**In Replit console, run:**
```bash
./backup.sh
```

**You'll see:**
```
🎉 BACKUP COMPLETE!
📁 Backup saved in: backup_20240115_143022
🔒 Your data is safe in: backup_20240115_143022
```

### Step 2: Upload to GitHub
1. Upload all new files to GitHub
2. In Replit: Update from GitHub (data will be wiped - that's OK!)

### Step 3: Restore (After GitHub Update)  
**In Replit console, run:**
```bash
./quick_restore.sh
```

**You'll see:**
```
🎉 RESTORE COMPLETE!
🛡️ Your bot now has automatic backup protection!
```

### Step 4: Start Bot
```bash
python main.py
```

## 🔧 Manual Method (If Scripts Don't Work)

### Manual Backup:
```bash
# Create backup folder
mkdir backup_manual

# Copy your data files
cp birthdays.db backup_manual/ 2>/dev/null || echo "No birthdays.db"
cp user_profiles.json backup_manual/ 2>/dev/null || echo "No user_profiles.json"
cp welcome_data.json backup_manual/ 2>/dev/null || echo "No welcome_data.json"
cp analytics.json backup_manual/ 2>/dev/null || echo "No analytics.json"
cp auction_data.json backup_manual/ 2>/dev/null || echo "No auction_data.json"

# Check what was backed up
ls -la backup_manual/
```

### Manual Restore (After GitHub Update):
```bash
# Copy files back
cp backup_manual/birthdays.db . 2>/dev/null && echo "✅ Restored birthdays.db"
cp backup_manual/user_profiles.json . 2>/dev/null && echo "✅ Restored user_profiles.json"
cp backup_manual/welcome_data.json . 2>/dev/null && echo "✅ Restored welcome_data.json"
cp backup_manual/analytics.json . 2>/dev/null && echo "✅ Restored analytics.json"
cp backup_manual/auction_data.json . 2>/dev/null && echo "✅ Restored auction_data.json"

# Start bot
python main.py
```

## 🎯 One-Line Commands

**Backup everything:**
```bash
mkdir backup_$(date +%Y%m%d_%H%M%S) && cp *.db *.json backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null; ls -la backup_*
```

**Restore everything (replace YYYYMMDD_HHMMSS with your backup folder):**
```bash
cp backup_YYYYMMDD_HHMMSS/* . 2>/dev/null && echo "✅ All files restored"
```

## 🆘 Emergency Commands

**Find your backups:**
```bash
ls -la backup_*
```

**See what's in a backup:**
```bash
ls -la backup_YYYYMMDD_HHMMSS/
```

**Copy specific file:**
```bash
cp backup_YYYYMMDD_HHMMSS/birthdays.db .
```

**Check if restore worked:**
```bash
ls -la *.db *.json
python backup_manager.py stats
```

## 🎉 After Migration

**Future GitHub updates are now safe:**
```bash
# Before updates:
python pre_update.py

# After GitHub update:
python main.py  # Auto-restores!
```

---

## 📋 Quick Checklist

**Before GitHub upload:**
- [ ] ✅ Run `./backup.sh` OR manual backup commands
- [ ] ✅ See "BACKUP COMPLETE!" message
- [ ] ✅ Upload to GitHub

**After GitHub update:**
- [ ] ✅ Run `./quick_restore.sh` OR manual restore commands  
- [ ] ✅ See "RESTORE COMPLETE!" message
- [ ] ✅ Run `python main.py`
- [ ] ✅ Verify bot works with your data

**You're now protected forever!** 🛡️