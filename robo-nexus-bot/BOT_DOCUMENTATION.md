# Robo Nexus Bot - Complete Documentation

## Overview
Discord bot for Robo Nexus robotics community with birthday tracking, auction system, and member verification.

---

## Features

### 🎂 Birthday System
- Register birthdays with `/register_birthday MM-DD`
- Automatic daily birthday announcements at 9:00 AM
- View upcoming birthdays with `/upcoming_birthdays`
- Birthday leaderboard with `/birthday_leaderboard`

### 🏷️ Auction System
- Create auctions with `/create_auction`
- Bid on items with `/bid`
- Buy now option with `/buy_now`
- View your auctions with `/my_auctions`
- Auction statistics with `/auction_stats`

### 👥 Welcome & Verification System
- Automatic welcome messages for new members
- Multi-stage verification process:
  1. Name & Class (required)
  2. Birthday (required)
  3. Email (optional)
  4. Phone (optional)
  5. Social links & portfolio (optional)
- Automatic class role assignment
- Profile management with `/view_profile` and `/update_profile`

### 🔧 Admin Commands
- `/set_birthday_channel` - Configure birthday announcements
- `/set_welcome_channel` - Configure welcome notifications
- `/set_self_roles_channel` - Configure verification channel
- `/reset_birthdays` - Delete all birthdays
- `/reset_auctions` - Delete all auctions
- `/reset_all_except_auctions` - Reset everything except auctions
- `/purge <count> [channel]` - Delete messages
- `/manual_verify @user` - Manually verify a member
- `/export_profiles` - Export all profiles to CSV

---

## Database (PostgreSQL)

### Tables:
1. **birthdays** - Birthday data
2. **auctions** - Auction listings
3. **bids** - Auction bids
4. **user_profiles** - User verification profiles
5. **welcome_data** - Welcome verification state
6. **settings** - Bot settings

### Connection:
```
postgresql://postgres:password@helium/heliumdb?sslmode=disable
```

All data is stored in Replit PostgreSQL database and never lost on code updates.

---

## Setup in Replit

### 1. Required Secrets:
```
DISCORD_TOKEN - Your bot token
DATABASE_URL - PostgreSQL connection string
GUILD_ID - Your Discord server ID
SESSION_SECRET - Random secret for web features
```

### 2. Run Setup:
```bash
python setup_replit.py
```

This will:
- Check PostgreSQL connection
- Create all database tables
- Migrate your data (if any)
- Verify everything is working

### 3. Start Bot:
```bash
python main.py
```

---

## Commands Reference

### Birthday Commands:
```
/register_birthday <date> - Register your birthday (MM-DD format)
/my_birthday - Check your registered birthday
/upcoming_birthdays - See upcoming birthdays
/birthday_leaderboard - See all birthdays sorted by month
/set_birthday_channel <channel> - [ADMIN] Set birthday announcement channel
/birthday_config - [ADMIN] View birthday configuration
/reset_birthdays - [ADMIN] Delete all birthdays
/test_birthday - [ADMIN] Manually trigger birthday check
```

### Auction Commands:
```
/create_auction - Create a new auction listing
/bid <auction_id> <amount> - Place a bid
/buy_now <auction_id> - Buy item at buy-now price
/my_auctions - View your auction listings
/auction_stats - View auction statistics
/reset_auctions - [ADMIN] Delete all auctions
```

### Welcome/Profile Commands:
```
/set_welcome_channel <channel> - [ADMIN] Set welcome notifications channel
/set_self_roles_channel <channel> - [ADMIN] Set verification channel
/welcome_config - [ADMIN] View welcome system configuration
/view_profile <user> - [ADMIN] View a user's profile
/update_profile <user> - [ADMIN] Update a user's profile
/manual_verify <user> - [ADMIN] Manually verify a user
/export_profiles - [ADMIN] Export all profiles to CSV
/birthday_collect <date> - Register birthday in self-roles channel
```

### Admin Commands:
```
/purge <count> [channel] - Delete messages (1-100)
/reset_all_except_auctions - Reset all data except auctions
/check_intents - Check if member intents are enabled
```

---

## File Structure

### Core Files:
- `main.py` - Bot entry point
- `bot.py` - Bot initialization and event handlers
- `config.py` - Configuration management
- `postgres_db.py` - PostgreSQL database interface
- `database.py` - Database wrapper for backward compatibility

### Command Files:
- `commands.py` - Birthday commands
- `admin_commands.py` - Admin commands
- `auction.py` - Auction system
- `welcome_system.py` - Welcome and verification system
- `help_commands.py` - Help commands
- `dev_commands.py` - Developer commands
- `github_integration.py` - GitHub notifications

### Utility Files:
- `date_parser.py` - Date parsing utilities
- `analytics.py` - Analytics and statistics
- `keep_alive.py` - Web server for uptime monitoring

### Setup Files:
- `setup_replit.py` - One-command setup script
- `reset_all_except_auctions.py` - Data reset script
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version

### Documentation:
- `README.md` - Project overview
- `BOT_DOCUMENTATION.md` - This file
- `COMPLETE_POSTGRESQL_MIGRATION.md` - Migration details
- `RESET_AND_COLLECT_GUIDE.md` - Data collection guide
- `DEPLOYMENT.md` - Deployment instructions
- `REPLIT_DEPLOY.md` - Replit-specific deployment
- `GITHUB_SETUP.md` - GitHub integration setup

---

## Deployment

### Replit (Recommended):
1. Fork/clone repository
2. Set up secrets (DISCORD_TOKEN, DATABASE_URL, etc.)
3. Run `python setup_replit.py`
4. Run `python main.py`
5. Keep bot running with "Always On" feature

### Railway:
1. Connect GitHub repository
2. Set environment variables
3. Deploy with `railway.toml` configuration

### Docker:
1. Build: `docker build -t robo-nexus-bot .`
2. Run: `docker run -e DISCORD_TOKEN=... robo-nexus-bot`

---

## Troubleshooting

### Bot Not Responding:
- Check bot is online
- Verify DISCORD_TOKEN is correct
- Check bot has proper permissions
- Verify member intents are enabled

### Database Errors:
- Check DATABASE_URL is correct
- Verify PostgreSQL is running
- Check connection with `python setup_replit.py`

### Welcome System Not Working:
- Set channels: `/set_welcome_channel` and `/set_self_roles_channel`
- Check bot permissions in those channels
- Verify member intents are enabled with `/check_intents`

### Birthday Announcements Not Sending:
- Set channel: `/set_birthday_channel`
- Check bot has send message permission
- Test manually with `/test_birthday`

---

## Data Management

### Backup Data:
```
/export_profiles - Export all user profiles to CSV
```

### Reset Data:
```
/reset_birthdays - Delete all birthdays
/reset_auctions - Delete all auctions
/reset_all_except_auctions - Reset everything except auctions
```

### Migrate Data:
All data is automatically migrated when you run `setup_replit.py`

---

## Development

### Adding New Commands:
1. Create command in appropriate cog file
2. Use `@app_commands.command()` decorator
3. Add to bot in `main.py`

### Database Changes:
1. Update schema in `postgres_db.py`
2. Add CRUD methods
3. Update `setup_replit.py` if needed

### Testing:
1. Test in development server first
2. Use `/test_birthday` for birthday testing
3. Check logs for errors

---

## Support

### Issues:
- Check logs in Replit console
- Review error messages
- Check bot permissions
- Verify database connection

### Contact:
- Discord: Robo Nexus server
- GitHub: Repository issues

---

## License
MIT License - See repository for details

---

## Version History

### v3.0 (Current) - PostgreSQL Migration
- ✅ All data stored in PostgreSQL
- ✅ Welcome system with verification
- ✅ Auction system
- ✅ Birthday system
- ✅ Admin commands
- ✅ Profile management
- ✅ Data export

### v2.0 - Feature Expansion
- Added auction system
- Added welcome system
- Added profile management

### v1.0 - Initial Release
- Basic birthday tracking
- Simple commands

---

**Last Updated:** January 29, 2026
