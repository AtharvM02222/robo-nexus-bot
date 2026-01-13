# 🔒 Replit Data Protection Guide

## Problem: GitHub Updates Wipe Databases

When you update your Replit from GitHub, it overwrites ALL files, including your databases with user data, birthdays, profiles, etc.

## ✅ Solution: Automatic Backup System

I've added a comprehensive backup system that protects your data automatically!

## 🛡️ Protection Features

### 1. **Automatic Backup on Startup**
- Bot creates backup every time it starts
- Stores backups outside the main code directory
- Backups survive GitHub updates

### 2. **Automatic Restore After Updates** 
- Bot detects missing databases on startup
- Automatically restores from latest backup
- No manual intervention needed

### 3. **Manual Backup Commands**
- Create backups before risky operations
- List and manage existing backups
- Restore specific backups when needed

## 📋 How to Use (Step by Step)

### Before Updating from GitHub:

**Option 1: Automatic (Recommended)**
```bash
# Just run this before updating
python pre_update.py
```

**Option 2: Manual**
```bash
# Create manual backup
python backup_manager.py backup "before_github_update"
```

### After Updating from GitHub:

**Just start the bot normally:**
```bash
python main.py
```

The bot will automatically:
1. ✅ Check if databases exist
2. 🔄 Restore from backup if missing  
3. 📊 Show what was restored
4. 🚀 Start normally with your data intact

## 🔧 Backup Commands Reference

### Create Backups
```bash
python backup_manager.py backup                    # Quick backup
python backup_manager.py backup "my_reason"        # Backup with reason
python pre_update.py                              # Pre-GitHub update backup
```

### Restore Backups
```bash
python backup_manager.py restore                   # Restore latest backup
python backup_manager.py restore /path/to/backup   # Restore specific backup
```

### Manage Backups
```bash
python backup_manager.py list                      # List all backups
python backup_manager.py stats                     # Show database statistics
python backup_manager.py check                     # Check database integrity
```

## 📁 What Gets Backed Up

All your important data files:
- `birthdays.db` - Birthday registrations and server configs
- `user_profiles.json` - Complete member profiles (name, class, email, social links)
- `welcome_data.json` - Welcome system configuration
- `analytics.json` - Bot usage analytics
- `auction_data.json` - Auction system data
- `deploy_info.json` - Deployment tracking

## 🗂️ Backup Storage Location

Backups are stored in: `/home/runner/robo_nexus_backups/`

This directory is OUTSIDE your main code folder, so it survives GitHub updates!

### Backup Folder Structure:
```
/home/runner/robo_nexus_backups/
├── backup_20240115_143022_startup/
│   ├── birthdays.db
│   ├── user_profiles.json
│   ├── welcome_data.json
│   └── backup_info.json
├── backup_20240115_150000_pre_github_update/
│   ├── birthdays.db
│   ├── user_profiles.json
│   └── backup_info.json
└── backup_20240115_160000_manual/
    └── ...
```

## 🚨 Emergency Recovery

If something goes wrong:

### 1. **Check Available Backups**
```bash
python backup_manager.py list
```

### 2. **Restore Specific Backup**
```bash
python backup_manager.py restore /home/runner/robo_nexus_backups/backup_YYYYMMDD_HHMMSS_reason/
```

### 3. **Check What Was Restored**
```bash
python backup_manager.py stats
```

## 🔄 Recommended Workflow

### Daily Operation:
1. ✅ Bot runs normally with automatic backups
2. ✅ Data is protected automatically

### Before GitHub Updates:
1. 🔄 Run: `python pre_update.py`
2. ✅ See "BACKUP SUCCESSFUL!" message
3. 🔄 Update from GitHub in Replit
4. 🚀 Run: `python main.py` (auto-restores if needed)

### Weekly Maintenance:
1. 📋 Run: `python backup_manager.py list`
2. 🧹 Keep recent backups, delete very old ones if needed

## 💡 Pro Tips

### 1. **Always Backup Before Major Changes**
```bash
python backup_manager.py backup "before_adding_new_feature"
```

### 2. **Check Your Data Regularly**
```bash
python backup_manager.py stats
```

### 3. **Test Restore Process**
```bash
# Create test backup
python backup_manager.py backup "test"

# Restore it to make sure it works
python backup_manager.py restore
```

### 4. **Monitor Backup Success**
The bot logs all backup operations. Check the console output for:
- ✅ "Backup created" messages
- ✅ "Restored X files" messages
- ❌ Any error messages

## 🛠️ Troubleshooting

### "No backup found to restore"
- You're starting fresh (no previous data)
- This is normal for first-time setup

### "Backup failed" 
- Check file permissions
- Ensure `/home/runner/` directory is writable
- Check available disk space

### "Restore failed"
- Backup files might be corrupted
- Try restoring from a different backup
- Check backup folder exists

### Missing Data After Update
1. Check if bot auto-restored: look for "Restored X files" message
2. If not, manually restore: `python backup_manager.py restore`
3. Check backup list: `python backup_manager.py list`

## 🎯 Success Indicators

You'll know the system is working when you see:

**On Startup:**
```
🔍 Checking database integrity...
✅ All database files present
📊 Database Status:
  • Birthdays: 15
  • User Profiles: 23
  • Servers Configured: 1
💾 Creating startup backup...
✅ Backup created: /home/runner/robo_nexus_backups/backup_20240115_143022_startup
```

**After GitHub Update:**
```
🔍 Checking database integrity...
⚠️ Missing database files detected: ['birthdays.db', 'user_profiles.json']
🔄 Attempting to restore from latest backup...
✅ Database files restored successfully!
📊 Database Status:
  • Birthdays: 15
  • User Profiles: 23
```

---

## 🎉 You're Protected!

With this system:
- ✅ Your data survives GitHub updates
- ✅ Automatic backup and restore
- ✅ Manual control when needed
- ✅ Multiple backup points
- ✅ Easy recovery process

**Never lose your Discord bot data again!** 🛡️