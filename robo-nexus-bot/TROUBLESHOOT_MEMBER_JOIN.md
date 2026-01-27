# Troubleshooting on_member_join Not Working

## The Problem
The `on_member_join` event is not triggering when new members join the server, even though:
- ✅ SERVER MEMBERS INTENT is enabled in Discord Developer Portal
- ✅ `intents.members = True` is in the code
- ✅ Welcome system cog is loaded
- ✅ `/manual_verify` command works

## Diagnosis Steps

### Step 1: Check if Intents are Actually Enabled in Running Bot
Run this command in Discord:
```
/check_intents
```

This will show you:
- ✅ or ❌ for Members Intent
- ✅ or ❌ for Message Content Intent
- Number of on_member_join listeners registered

**Expected Result:**
- Members Intent: ✅ Enabled
- on_member_join Listeners: ✅ 1 registered

**If Members Intent shows ❌ DISABLED:**
The bot is running OLD CODE that doesn't have `intents.members = True`. You need to do a HARD RESTART (see Step 2).

### Step 2: Hard Restart in Replit (NOT /restart command)

The `/restart` command might not reload the code properly. Do a FULL republish:

1. **Stop the bot completely** in Replit:
   - Click the "Stop" button in Replit
   - Wait for it to fully stop

2. **Republish the bot**:
   - Click "Run" or "Deploy" again
   - Wait for all cogs to load
   - Look for this log: `welcome_system - INFO - Welcome system cog loaded`

3. **Test again**:
   - Have someone leave and rejoin the server
   - Check logs for: `New member joined: [username]`

### Step 3: Verify Code is Actually Deployed

Check if the code has `intents.members = True`:

```bash
cd ~/workspace/robo-nexus-bot/robo-nexus-birthday-bot
grep -n "intents.members" bot.py
```

**Expected output:**
```
28:        intents.members = True  # Required to detect member joins!
```

If you don't see this line, the code didn't update. You need to:
1. Pull from GitHub again: `git pull origin main`
2. Republish the bot

### Step 4: Check Logs When Member Joins

When someone joins, you should see this in the logs:
```
welcome_system - INFO - New member joined: [username] ([user_id])
```

**If you DON'T see this log:**
- The `on_member_join` event is not firing
- This means intents aren't actually enabled in the running bot
- Go back to Step 2 and do a hard restart

**If you DO see this log but no DM is sent:**
- The event is firing but there's an error in the welcome process
- Check for error logs after the "New member joined" message

## Common Issues

### Issue 1: Bot Using Cached Code
**Symptom:** `/check_intents` shows Members Intent disabled
**Solution:** Hard restart (Step 2)

### Issue 2: Discord Developer Portal Not Saved
**Symptom:** Intents show enabled in code but event doesn't fire
**Solution:** 
1. Go to Discord Developer Portal
2. Go to your bot application
3. Click "Bot" section
4. Scroll to "Privileged Gateway Intents"
5. Make sure "SERVER MEMBERS INTENT" has a checkmark
6. Click "Save Changes" at the bottom
7. Hard restart the bot

### Issue 3: Bot Doesn't Have Permission to See Members
**Symptom:** Bot can't fetch member list
**Solution:** 
1. Check bot has "View Server Members" permission
2. Bot should have Administrator permission (which includes this)

## Quick Test

After fixing, test with this sequence:

1. Run `/check_intents` - should show Members Intent ✅
2. Have someone leave the server
3. Have them rejoin
4. Check logs for "New member joined"
5. Check if they received a DM or message in #self-roles

## Still Not Working?

If after all these steps it still doesn't work:

1. **Check bot logs** for any errors
2. **Verify in Discord Developer Portal** that SERVER MEMBERS INTENT is ON
3. **Try creating a test bot** with just the member join event to isolate the issue
4. **Check Discord API status** - sometimes Discord has issues with intents

## Success Indicators

You'll know it's working when:
- ✅ `/check_intents` shows Members Intent enabled
- ✅ Logs show "New member joined" when someone joins
- ✅ New member receives DM or message in #self-roles
- ✅ Welcome notification appears in welcome channel
