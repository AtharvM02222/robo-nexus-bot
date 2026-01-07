# 🚀 Replit Deployment Guide - FREE 24/7 Hosting

## Why Replit for Students?

✅ **Completely FREE** - No credit card needed
✅ **24/7 hosting** with keep-alive system
✅ **Instant deployment** - Works in minutes
✅ **Student-friendly** - Perfect for learning
✅ **Built-in editor** - Edit code directly online
✅ **Automatic restarts** - Bot stays online

## Step-by-Step Deployment

### 1. **Create Replit Account**

1. Go to [replit.com](https://replit.com)
2. Click "Sign up"
3. **Use "Continue with GitHub"** (use your student account)
4. This gives you better benefits!

### 2. **Create New Repl**

1. Click **"Create Repl"**
2. Select **"Import from GitHub"**
3. **OR** select **"Python"** template and upload files

### 3. **Upload Your Bot Files**

**If using template:**
1. Delete default files
2. Upload all files from `robo-nexus-birthday-bot/` folder
3. Make sure you have:
   - `main.py`
   - `bot.py`
   - `requirements.txt`
   - `keep_alive.py`
   - All other `.py` files

### 4. **Set Environment Variables (CRITICAL)**

1. **Click the 🔒 "Secrets" tab** (left sidebar)
2. **Add these secrets:**

   ```
   Key: DISCORD_TOKEN
   Value: your_regenerated_bot_token_here

   Key: GUILD_ID  
   Value: 1403310542030114898

   Key: DATABASE_PATH
   Value: birthdays.db

   Key: BOT_NAME
   Value: Robo Nexus

   Key: BIRTHDAY_CHECK_TIME
   Value: 09:00
   ```

3. **IMPORTANT:** Use your NEW regenerated Discord bot token!

### 5. **Install Dependencies**

1. **Click "Shell" tab** (terminal icon)
2. **Run:** `pip install -r requirements.txt`
3. **Wait for installation to complete**

### 6. **Run Your Bot**

1. **Click the big green "Run" button** ▶️
2. **You should see:**
   ```
   🤖 Starting Robo Nexus Birthday Bot...
   🌐 Keep-alive server started on port 8080
   🚀 Connecting to Discord...
   🤖 Robo Nexus is now online!
   ```

### 7. **Keep Bot Alive 24/7**

**The keep-alive system is already built in!**

- ✅ **Web server runs on port 8080**
- ✅ **Prevents Replit from sleeping**
- ✅ **Shows bot status at your Repl URL**
- ✅ **Automatic restart if bot crashes**

### 8. **Test Your Bot**

**In your Discord server:**

1. **Set birthday channel:**
   ```
   /set_birthday_channel channel:#birthdays
   ```

2. **Test commands:**
   ```
   /birthday_help
   /register_birthday date:12-25
   /my_birthday
   ```

3. **Check bot status:**
   - Visit your Repl URL (shows in address bar)
   - Should show "Bot is running and healthy!"

## 🔧 Troubleshooting

### **Bot not starting:**
- Check Secrets are set correctly
- Verify bot token is valid (regenerate if needed)
- Check Console tab for error messages

### **Commands not appearing:**
- Wait 5-10 minutes for Discord to sync
- Restart the Repl
- Check bot has Administrator permissions

### **Bot goes offline:**
- Replit may sleep after inactivity
- The keep-alive system should prevent this
- If it happens, just click "Run" again

### **Database issues:**
- Replit automatically handles file persistence
- Database file is saved in your Repl

## 🎯 Replit Benefits for Students

### **Free Features:**
- ✅ **Always-on Repls** - Bot runs 24/7
- ✅ **Unlimited public Repls**
- ✅ **Built-in database storage**
- ✅ **Collaborative editing**
- ✅ **Version control**

### **Student Perks:**
- 🎓 **GitHub Student Pack** may include Replit benefits
- 🎓 **Educational discounts** available
- 🎓 **Learning resources** and tutorials

## 📊 Monitoring Your Bot

### **Repl Dashboard:**
- **Console:** Real-time logs and errors
- **Files:** Edit code directly online
- **Shell:** Run commands and debug
- **Secrets:** Manage environment variables

### **Web Interface:**
- Visit your Repl URL to see bot status
- Shows: "Bot is running and healthy!"
- Health check endpoint: `/health`

### **Discord:**
- Bot appears online in your server
- Commands work immediately
- Birthday announcements at 9:00 AM daily

## 🔄 Updating Your Bot

### **Edit Code:**
1. Click on any `.py` file in Repl
2. Make your changes
3. Click "Run" to restart with changes

### **Add Features:**
1. Edit the appropriate command file
2. Test locally in Repl
3. Bot automatically restarts

## 💡 Pro Tips

### **Keep Repl Active:**
- The keep-alive system handles this automatically
- Visit your Repl URL occasionally
- Pin the tab in your browser

### **Monitor Usage:**
- Check Console tab for logs
- Watch for error messages
- Monitor bot's Discord status

### **Backup Your Code:**
- Replit has built-in version control
- Download files periodically
- Consider syncing with GitHub

---

## 🎉 **Your Bot is Now Running 24/7 for FREE!**

**What happens next:**
- ✅ Bot checks for birthdays daily at 9:00 AM
- ✅ Sends "Hey Robo Nexus, it's @user's birthday today! 🎉"
- ✅ Handles all slash commands
- ✅ Stores birthdays permanently
- ✅ Restarts automatically if needed
- ✅ Runs completely free on Replit!

**Need help?** Check the Console tab in Replit or test commands in Discord!

---

**🎓 Student Tip:** While using Replit, also apply for Railway Student credits and Heroku credits through GitHub Student Pack for even more hosting options!