# Robo Nexus Birthday Bot 🎉

A Discord bot for managing birthday celebrations in the Robo Nexus server. Automatically sends birthday messages and allows members to register their birthdays.

## 🚀 **DEPLOYED ON RAILWAY - 24/7 OPERATION**

This bot is designed for Railway deployment and runs 24/7 without requiring your computer to stay on.

## Features

- 🎂 Birthday registration with flexible date formats
- 🎉 Automatic daily birthday notifications at 9:00 AM
- 📅 Birthday lookup and management commands
- 🔧 Admin configuration for birthday channels
- 💾 Persistent SQLite database storage
- ☁️ Railway cloud deployment ready
- 🤖 Administrator permissions for full functionality

## Quick Start

### 1. **Deploy to Railway (Recommended)**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

**Or follow the detailed [DEPLOYMENT.md](DEPLOYMENT.md) guide**

### 2. **Local Testing (Optional)**

```bash
# Clone and setup
git clone <your-repo>
cd robo-nexus-birthday-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your bot token and server ID

# Run locally
python main.py
```

## Bot Commands

### 👥 **User Commands**
- `/register_birthday` - Register your birthday
- `/my_birthday` - Check your registered birthday
- `/check_birthday` - Look up someone's birthday
- `/upcoming_birthdays` - See all upcoming birthdays
- `/remove_birthday` - Remove your birthday
- `/birthday_help` - Show all commands

### ⚙️ **Admin Commands**
- `/set_birthday_channel` - Set birthday announcement channel
- `/birthday_config` - View bot configuration

## 📅 Supported Date Formats

- **MM-DD** (e.g., `12-25` for December 25)
- **MM/DD** (e.g., `12/25` for December 25)
- **MM-DD-YYYY** (e.g., `12-25-1995`)
- **MM/DD/YYYY** (e.g., `12/25/1995`)

## 🎉 How It Works

1. **Setup:** Admin uses `/set_birthday_channel` to configure announcement channel
2. **Registration:** Users register birthdays with `/register_birthday`
3. **Daily Check:** Bot automatically checks for birthdays at 9:00 AM
4. **Announcements:** Sends messages like: "Hey Robo Nexus, it's @username's birthday today! 🎉"

## 🔧 Configuration

### Environment Variables (Railway)

```
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=1403310542030114898
DATABASE_PATH=birthdays.db
BOT_NAME=Robo Nexus
BIRTHDAY_CHECK_TIME=09:00
```

### Discord Bot Setup

1. **Create Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application named "Robo Nexus"
   - Go to Bot section → Create bot → Copy token

2. **Invite Bot to Server:**
   - Go to OAuth2 → URL Generator
   - Select: `bot` + `applications.commands`
   - Select: `Administrator` permissions
   - Use generated URL to invite bot

3. **Configure in Discord:**
   - Use `/set_birthday_channel` to set announcement channel
   - Test with `/birthday_help`

## 📊 Railway Deployment Benefits

- ✅ **24/7 Operation** - No need to keep your computer on
- ✅ **Free Tier** - 500 hours/month (covers 24/7 usage)
- ✅ **Auto-restart** - Bot restarts automatically if it crashes
- ✅ **Persistent Database** - SQLite data persists across restarts
- ✅ **Easy Updates** - Push to GitHub → auto-deploy
- ✅ **Monitoring** - Full logs and metrics dashboard

## 🛠️ Development

### Project Structure

```
robo-nexus-birthday-bot/
├── main.py              # Entry point
├── bot.py               # Main bot class
├── config.py            # Configuration management
├── database.py          # SQLite database manager
├── date_parser.py       # Date parsing utilities
├── commands.py          # User slash commands
├── admin_commands.py    # Admin slash commands
├── help_commands.py     # Help system
├── requirements.txt     # Python dependencies
├── railway.toml         # Railway deployment config
├── .env                 # Environment variables (local)
└── DEPLOYMENT.md        # Deployment guide
```

### Adding New Features

1. **New Commands:** Add to appropriate `*_commands.py` file
2. **Database Changes:** Update `database.py` schema
3. **Configuration:** Add to `config.py` and `.env.example`
4. **Deploy:** Push to GitHub (auto-deploys to Railway)

## 🔍 Troubleshooting

**Bot not responding:**
- Check Railway logs for errors
- Verify environment variables are set
- Ensure bot has Administrator permissions

**Commands not appearing:**
- Wait 5-10 minutes for slash command sync
- Restart bot deployment on Railway
- Check bot is in your server

**Birthday notifications not working:**
- Verify `/set_birthday_channel` is configured
- Check bot has permissions in announcement channel
- Confirm users have registered birthdays

## 📈 Monitoring

**Railway Dashboard:**
- View real-time logs
- Monitor resource usage
- Track deployment history
- Check uptime statistics

**Discord:**
- Bot online status
- Command response times
- Daily birthday announcements

## 🎯 Future Enhancements

- 🎊 Birthday role assignments
- 🎁 Birthday reminder DMs
- 📊 Birthday statistics
- 🎨 Custom birthday messages
- 🌍 Timezone support
- 📅 Birthday countdown features

---

**Built for the Robo Nexus Discord community 🤖**

**Deployed on Railway ⚡ | Running 24/7 ☁️ | Administrator Permissions 🔐**