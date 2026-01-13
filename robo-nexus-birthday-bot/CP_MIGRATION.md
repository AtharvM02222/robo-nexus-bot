# 🚀 Simple cp Migration Guide

## The Plan
Use simple `cp` commands to backup and restore your data when uploading to GitHub.

## 📋 Step-by-Step Commands

### STEP 1: Backup (Before GitHub Upload)

**In your current Replit shell:**
```bash
mkdir my_backup
cp *.db *.json my_backup/
ls my_backup/
```

**You should see output like:**
```
analytics.json
auction_data.json  
birthdays.db
deploy_info.json
user_profiles.json
welcome_data.json
```

### STEP 2: Upload to GitHub
1. Commit and push all your new code to GitHub
2. In Replit: Update from GitHub (your databases will be wiped)

### STEP 3: Restore (After GitHub Update)

**In Replit shell:**
```bash
cp my_backup/* .
ls *.db *.json
```

**You should see your files are back:**
```
analytics.json
auction_data.json
birthdays.db  
deploy_info.json
user_profiles.json
welcome_data.json
```

### STEP 4: Start Bot
```bash
python main.py
```

**You should see:**
```
📁 Found backup folder(s): my_backup
📊 Current database files: 6 found
  • analytics.json (117 bytes)
  • auction_data.json (66 bytes)
  • birthdays.db (12288 bytes)
  • deploy_info.json (136 bytes)
  • user_profiles.json (2048 bytes)
  • welcome_data.json (256 bytes)
🤖 Starting Robo Nexus Birthday Bot...
🚀 Connecting to Discord...
```

## 🎯 What Gets Backed Up & Restored

**All your important data:**
- ✅ `birthdays.db` - Birthday registrations
- ✅ `user_profiles.json` - Member profiles (names, emails, social links)  
- ✅ `analytics.json` - Bot usage statistics
- ✅ `auction_data.json` - Auction items and bids
- ✅ `welcome_data.json` - Welcome system config
- ✅ `deploy_info.json` - Deployment tracking

## 🆘 Troubleshooting

**If backup folder is missing after GitHub update:**
```bash
ls -d */  # Find your backup folder
cp backup_folder_name/* .  # Restore from it
```

**If some files are missing:**
```bash
# Check what you have in backup
ls my_backup/

# Copy specific files
cp my_backup/birthdays.db .
cp my_backup/user_profiles.json .
```

**If restore didn't work:**
```bash
# Check current files
ls *.db *.json

# Check backup files  
ls my_backup/

# Copy again
cp my_backup/* . 2>/dev/null
```

## 🎉 After Migration

**Your bot now has the enhanced features:**
- 3-stage welcome system (name, email, social links)
- Complete member profiles
- All your existing data preserved

**Future GitHub updates:** The bot will remind you to backup, but you can always use the same simple commands:
```bash
# Before update:
cp *.db *.json my_backup/

# After update:  
cp my_backup/* .
```

---

## 📝 Quick Reference

**Backup:** `mkdir my_backup && cp *.db *.json my_backup/`

**Restore:** `cp my_backup/* .`

**Check:** `ls *.db *.json`

**Start:** `python main.py`

**Simple and bulletproof!** 🛡️