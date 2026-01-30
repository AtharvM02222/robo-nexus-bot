# Reset and Collect Fresh Data Guide

## Your Plan ✅
Reset all data EXCEPT auctions, then collect fresh info from members as they rejoin.

---

## Option 1: Reset via Discord Command (RECOMMENDED)

### Step 1: Run the Reset Command
In Discord, type:
```
/reset_all_except_auctions
```

### Step 2: Confirm
- Bot will show what will be deleted and what will be kept
- Type `CONFIRM` within 30 seconds to proceed
- All birthdays, profiles, and welcome data will be deleted
- Your 4 auctions will remain safe ✅

---

## Option 2: Reset via Python Script

### In Replit Shell:
```bash
cd robo-nexus-bot/robo-nexus-bot
python reset_all_except_auctions.py
```

### Confirmation:
- Script will ask: "Are you sure you want to continue? (yes/no)"
- Type `yes` to proceed
- All data except auctions will be deleted

---

## What Gets Deleted ❌

### Birthdays:
- All 6 birthdays will be removed
- Members will register new birthdays during verification

### User Profiles:
- All verified user profiles will be removed
- Members will create new profiles during verification

### Welcome Data:
- All pending verification data will be removed
- Fresh verification flow for all members

---

## What Stays Safe ✅

### Auctions (4 total):
```
1. CT-6b (₹2,222 - ₹2,499)
2. 300 rpm johnson motor (₹1,299 - ₹1,499)
3. planetary 500rpm (₹1,499 - ₹1,699)
4. Nylon wheels (₹2,399 - ₹2,599)
```

### Bids:
- All existing bids on auctions remain intact

---

## After Reset: Member Collection Process

### Step 1: Remove Members from Server
1. Go to Discord server settings
2. Members tab
3. Remove all members (except yourself and the bot)
4. Keep a list of who to re-invite

### Step 2: Add Members Back One at a Time
1. Send invite link to first member
2. Wait for them to join
3. Bot will automatically send welcome message in #self-roles channel

### Step 3: Member Verification Flow
Bot will collect this info from each member:

#### Stage 1: Name & Class
```
Bot asks: "Please provide your name and class"
Member replies: "John Smith, Class 10"
```

#### Stage 2: Birthday
```
Bot asks: "Please share your birthday (MM-DD format)"
Member replies: "03-15"
Bot confirms: "Birthday registered: March 15"
```

#### Stage 3: Email (Optional)
```
Bot asks: "Please provide your Gmail address"
Member replies: "john.smith@gmail.com" or "skip"
```

#### Stage 4: Phone (Optional)
```
Bot asks: "Please share your phone number"
Member replies: "9876543210" or "skip"
```

#### Stage 5: Social Links (Optional)
```
Bot asks: "Please share your social media links & portfolio"
Member replies:
"Portfolio: johnsmith.dev
GitHub: github.com/johnsmith
LinkedIn: linkedin.com/in/johnsmith"
or "skip"
```

#### Stage 6: Complete ✅
```
Bot assigns class role
Bot saves all data to PostgreSQL
Member gets full server access
```

### Step 4: Repeat for Each Member
- Add next member
- Wait for verification to complete
- Add next member
- Continue until all members are back

---

## Data Collection Summary

### What Bot Collects:
- ✅ Name (required)
- ✅ Class/Grade (required)
- ✅ Birthday (required)
- ⭕ Email (optional)
- ⭕ Phone (optional)
- ⭕ Social Links (optional)
- ⭕ Portfolio Website (optional but recommended)

### Where Data is Stored:
- 🗄️ PostgreSQL database (Replit)
- 🔒 Never lost on code updates
- 💾 Automatically backed up
- 🚀 Fast and reliable

---

## Verification Commands

### For Members:
```
/birthday_collect MM-DD - Register birthday in self-roles channel
```

### For Admins:
```
/view_profile @user - View a member's profile
/update_profile @user - Update a member's info
/manual_verify @user - Manually verify a member
/export_profiles - Export all profiles to CSV
/welcome_config - View welcome system settings
```

---

## Tips for Smooth Collection

### 1. Set Channels First
```
/set_welcome_channel #welcome
/set_self_roles_channel #self-roles
```

### 2. Add Members Slowly
- Don't rush
- Wait for each verification to complete
- Ensure data is saved before adding next member

### 3. Help Members
- Some may not understand the format
- Guide them through each step
- Use `/manual_verify` if needed

### 4. Verify Data
- Use `/view_profile @user` to check collected data
- Use `/export_profiles` to get CSV of all data
- Ensure everything is correct

---

## Troubleshooting

### Member Doesn't Receive Welcome Message:
- Check if #self-roles channel is set: `/welcome_config`
- Set it if needed: `/set_self_roles_channel #self-roles`

### Member Makes a Mistake:
- Use `/update_profile @user` to fix their info
- Or use `/manual_verify @user` to re-verify them

### Bot Doesn't Respond:
- Check bot is online
- Check bot has permissions in #self-roles channel
- Check member intents are enabled

### Data Not Saving:
- Check PostgreSQL connection
- Check bot logs for errors
- Restart bot if needed

---

## Expected Timeline

### For 20 Members:
- ~5 minutes per member (including verification)
- Total: ~1.5-2 hours

### For 50 Members:
- ~5 minutes per member
- Total: ~4-5 hours

### Tips to Speed Up:
- Have members ready with their info
- Send them a template beforehand
- Use `/manual_verify` for bulk entry if needed

---

## After Collection Complete

### Verify Everything:
```
/export_profiles - Get CSV of all data
/upcoming_birthdays - Check all birthdays registered
/welcome_config - Verify settings
```

### Your Database Will Have:
- ✅ All member profiles
- ✅ All birthdays
- ✅ All contact info
- ✅ All social links
- ✅ Your 4 auctions (safe!)

---

## Commands Summary

### Reset Commands:
```
/reset_all_except_auctions - Reset everything except auctions (Discord)
python reset_all_except_auctions.py - Reset via script (Replit)
```

### Verification Commands:
```
/set_welcome_channel #channel - Set welcome notifications channel
/set_self_roles_channel #channel - Set verification channel
/welcome_config - View configuration
/view_profile @user - View member profile
/update_profile @user - Update member info
/manual_verify @user - Manually verify member
/export_profiles - Export all profiles to CSV
```

### Birthday Commands:
```
/register_birthday MM-DD - Register birthday
/my_birthday - Check your birthday
/upcoming_birthdays - See upcoming birthdays
/birthday_leaderboard - See all birthdays
```

---

## Ready to Start?

### Checklist:
- [ ] Bot is running
- [ ] Channels are configured (`/welcome_config`)
- [ ] You understand the verification flow
- [ ] You have list of members to re-invite
- [ ] You're ready to spend 1-5 hours collecting data

### When Ready:
1. Run `/reset_all_except_auctions` in Discord
2. Type `CONFIRM` to proceed
3. Remove all members from server
4. Start adding them back one by one
5. Guide each through verification
6. Verify data is collected correctly

---

## Good Luck! 🚀

Your 4 auctions are safe. All member data will be fresh and clean. Take your time and ensure quality data collection!
