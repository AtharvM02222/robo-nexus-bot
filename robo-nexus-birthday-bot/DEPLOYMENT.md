# 🚀 Railway Deployment Guide for Robo Nexus Birthday Bot

## Step-by-Step Railway Deployment

### 1. **Prepare Your Code**

**First, regenerate your bot token (IMPORTANT!):**
1. Go to Discord Developer Portal → Your "Robo Nexus" app → Bot
2. Click "Reset Token" and copy the new token
3. Keep this token safe - you'll need it for Railway

### 2. **Create Railway Account**

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended) or email
3. Verify your account

### 3. **Deploy to Railway**

**Option A: Deploy from GitHub (Recommended)**

1. **Push your code to GitHub:**
   ```bash
   cd robo-nexus-birthday-bot
   git init
   git add .
   git commit -m "Initial Robo Nexus Birthday Bot"
   # Create a new repository on GitHub, then:
   git remote add origin https://github.com/yourusername/robo-nexus-birthday-bot.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app/new](https://railway.app/new)
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect it's a Python project

**Option B: Deploy from Local Files**

1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo" → "Deploy from local directory"
3. Upload your `robo-nexus-birthday-bot` folder

### 4. **Configure Environment Variables**

After deployment, you need to set your environment variables:

1. **In Railway Dashboard:**
   - Go to your project
   - Click "Variables" tab
   - Add these variables:

   ```
   DISCORD_TOKEN = your_new_regenerated_token_here
   GUILD_ID = 1403310542030114898
   DATABASE_PATH = birthdays.db
   BOT_NAME = Robo Nexus
   BIRTHDAY_CHECK_TIME = 09:00
   ```

2. **Click "Deploy" after adding variables**

### 5. **Verify Deployment**

1. **Check Logs:**
   - Go to "Deployments" tab
   - Click on the latest deployment
   - Check logs for:
     ```
     🤖 Robo Nexus is now online!
     🎉 Robo Nexus Birthday Bot is ready!
     ```

2. **Test in Discord:**
   - Your bot should appear online in your server
   - Try `/birthday_help` to test commands

### 6. **Set Up Your Bot in Discord**

1. **Configure Birthday Channel:**
   ```
   /set_birthday_channel channel:#your-birthday-channel
   ```

2. **Test Registration:**
   ```
   /register_birthday date:12-25
   /my_birthday
   ```

## 🎯 Railway Benefits

✅ **Free Tier:** 500 hours/month (24/7 coverage)
✅ **Auto-restart:** Bot restarts if it crashes
✅ **Easy updates:** Push to GitHub → auto-deploy
✅ **Persistent storage:** SQLite database persists
✅ **Logs:** Full logging and monitoring
✅ **Custom domain:** Optional custom domain support

## 🔧 Troubleshooting

**Bot not starting:**
- Check environment variables are set correctly
- Verify bot token is valid and not expired
- Check deployment logs for errors

**Commands not working:**
- Wait 5-10 minutes for slash commands to sync
- Verify bot has Administrator permissions
- Check bot is in your server

**Database issues:**
- Railway automatically handles SQLite persistence
- Database file is stored in `/app/birthdays.db`

## 📊 Monitoring Your Bot

**Railway Dashboard:**
- **Metrics:** CPU, memory, network usage
- **Logs:** Real-time bot logs
- **Deployments:** Deployment history
- **Usage:** Track your free tier usage

**Discord:**
- Bot status (online/offline)
- Command responses
- Birthday announcements at 9:00 AM daily

## 🔄 Updating Your Bot

**From GitHub:**
1. Make changes to your code
2. Push to GitHub: `git push`
3. Railway auto-deploys the changes

**Manual Update:**
1. Upload new files to Railway
2. Redeploy from dashboard

## 💰 Cost Information

**Free Tier:**
- 500 execution hours/month
- Enough for 24/7 bot operation
- No credit card required

**Pro Plan ($5/month):**
- Unlimited execution hours
- Priority support
- Advanced features

---

🎉 **Your Robo Nexus Birthday Bot will be running 24/7 on Railway!**

The bot will automatically:
- Check for birthdays daily at 9:00 AM
- Send birthday messages to your configured channel
- Handle all user registrations and commands
- Restart automatically if any issues occur

**Need help?** Check the Railway logs or Discord bot status!