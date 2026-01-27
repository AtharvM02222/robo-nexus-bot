# 👋 Enhanced Welcome System Setup Guide

## Overview

The Robo Nexus Welcome System now features a comprehensive 3-stage onboarding process:
- **Stage 1:** Name and Class collection
- **Stage 2:** Gmail address collection  
- **Stage 3:** Social media links (optional)

The system automatically handles new member onboarding by:
- Restricting new members to only the self-roles channel initially
- Collecting complete profile information via DM or self-roles channel
- Auto-assigning class roles (6, 7, 8, 9, 10, 11, 12)
- Storing user profiles for team management
- Granting full server access after verification

## 🚀 Quick Setup

### 1. **Configure Channels**

```
/set_welcome_channel channel:#welcome
/set_self_roles_channel channel:#self-roles
```

### 2. **Set Up Channel Permissions**

**For #self-roles channel:**
- New members: ✅ View Channel, ✅ Send Messages
- Everyone else: ✅ View Channel, ❌ Send Messages
- Bot: ✅ All permissions

**For other channels:**
- New members: ❌ View Channel (until they get class role)
- Class roles (6, 7, 8, 9, 10, 11, 12): ✅ View Channel
- Bot: ✅ All permissions

### 3. **Test the System**

1. Create a test account or ask someone to join
2. Check they only see #self-roles channel
3. Verify they receive a DM from the bot
4. Test the 3-stage verification process

## 📋 Detailed Configuration

### Channel Setup

**#welcome (Welcome Notifications)**
- Purpose: Admin notifications about new members
- Permissions: Admin/Mod only
- Bot posts: Join notifications, verification status

**#self-roles (Initial Access)**
- Purpose: Where new members can interact initially
- Permissions: New members can send messages here only
- Bot posts: Welcome messages if DM fails

### Role Configuration

The bot automatically creates class roles if they don't exist:
- **6, 7, 8, 9, 10, 11, 12** (role names)
- Color: Blue
- Mentionable: Yes
- Position: Below admin roles

### Permission Structure

```
@everyone (new members)
├── #self-roles ✅ (can view & send)
└── Other channels ❌ (no access)

@6, @7, @8, @9, @10, @11, @12 (class roles)
├── #self-roles ✅ (can view, cannot send)
├── #general ✅ (full access)
├── #robotics ✅ (full access)
└── All other channels ✅ (full access)
```

## 🤖 Enhanced User Experience (3-Stage Process)

### 1. **User Joins Server**
- Sees only #self-roles channel
- Receives DM from bot with instructions

### 2. **Stage 1: Name & Class**
```
🎉 Welcome to Robo Nexus!

📝 Step 1: Basic Info
To get started, please provide:
1. Your Name
2. Your Class/Grade (6, 7, 8, 9, 10, 11, or 12)

💡 Example: "John Smith, Class 10"

🔄 What's Next?
After this, I'll ask for:
• Your Gmail address
• Social media links (optional)
```

**User responds:** `John Smith, Class 10`

### 3. **Stage 2: Gmail Address**
```
📧 Step 2: Gmail Address
Great! Welcome John Smith from Class 10!

📮 Please provide your Gmail address
We need your Gmail for:
• Team communications
• Project updates  
• Important announcements

💡 Example: john.smith@gmail.com

🔒 Privacy: Your email will only be used for Robo Nexus activities
```

**User responds:** `john.smith@gmail.com`

### 4. **Stage 3: Social Links (Optional)**
```
🔗 Step 3: Social Media Links (Optional)
Almost done! Please share your social media profiles:

🌐 Supported Platforms
• GitHub - Your coding projects
• LinkedIn - Professional profile
• YouTube - Your channel
• Spotify - Music profile

💡 Example Response:
GitHub: github.com/johnsmith
LinkedIn: linkedin.com/in/johnsmith
YouTube: youtube.com/@johnsmith

⚡ Quick Option: Type "skip" or "none" if you don't have any links
```

**User responds:** 
```
GitHub: github.com/johnsmith
LinkedIn: linkedin.com/in/johnsmith
```

### 5. **Verification Complete**
```
✅ Welcome Complete!
Welcome to Robo Nexus, John Smith!

🎓 Profile Summary
Name: John Smith
Class: 10
Email: john.smith@gmail.com

🔗 Social Links
GitHub: https://github.com/johnsmith
LinkedIn: https://linkedin.com/in/johnsmith

🚀 What's Next?
• Explore all server channels
• Join your classmates
• Participate in robotics discussions!
• Register your birthday with /register_birthday
```

## 🔧 Enhanced Admin Commands

### Configuration Commands
```
/set_welcome_channel #welcome          # Set welcome notifications channel
/set_self_roles_channel #self-roles    # Set initial access channel
/welcome_config                        # View current configuration
```

### Profile Management Commands
```
/view_profile @user                    # View complete user profile
/manual_verify @user "Name" 10 "email@gmail.com"  # Manually verify a user
```

## 🎯 Smart Recognition Features

### Class Recognition
The bot understands various formats:

**Numbers:** `6`, `7`, `8`, `9`, `10`, `11`, `12`

**Ordinals:** `6th`, `7th`, `8th`, `9th`, `10th`, `11th`, `12th`

**Words:** `sixth`, `seventh`, `eighth`, `ninth`, `tenth`, `eleventh`, `twelfth`

**With Context:** 
- `Class 10`
- `Grade 8`
- `I'm in 12th`
- `seventh grade`

### Email Validation
- **Must be Gmail:** Only @gmail.com addresses accepted
- **Format validation:** Proper email format required
- **Privacy assured:** Used only for Robo Nexus activities

### Social Links Detection
- **GitHub:** github.com/username
- **LinkedIn:** linkedin.com/in/username
- **YouTube:** youtube.com/@username or youtu.be links
- **Spotify:** open.spotify.com/user/username
- **Flexible format:** Works with or without "https://"
- **Optional:** Users can skip with "none", "skip", "n/a"

## 🛠️ Troubleshooting

**User not getting DM:**
- Bot sends message in #self-roles channel instead
- User can respond there for all stages

**Email not accepted:**
- Must be @gmail.com address
- Check for typos in email format
- Bot provides clear error messages

**Social links not recognized:**
- Supported platforms: GitHub, LinkedIn, YouTube, Spotify
- Can include platform name: "GitHub: github.com/user"
- Users can always skip this step

**Role not assigned:**
- Check bot has Manage Roles permission
- Ensure bot role is above class roles
- Check logs with `/error_log`
- Use `/manual_verify` if needed

## 📊 Enhanced Monitoring

### Welcome Channel Notifications
- New member joins
- Stage completion updates
- Final verification confirmations
- Complete profile summaries

### Profile Storage
- Complete user profiles saved to `user_profiles.json`
- Includes: name, class, email, social links, timestamps
- Admin access via `/view_profile` command

### Analytics Integration
- Verification completion rates
- Stage drop-off analysis
- Profile completeness statistics

## 🎨 Customization Options

### Profile Data Usage
The collected profiles can be used for:
- **Team website:** Auto-generate team member pages
- **Contact directory:** Internal team communications
- **Project assignments:** Match skills with GitHub profiles
- **Networking:** Connect members via LinkedIn
- **Content sharing:** Showcase member YouTube channels

### Integration Possibilities
- Export profiles to team website JSON
- Sync with Google Workspace
- Generate team contact sheets
- Create skill-based project groups

---

🎉 **Your Robo Nexus server now has comprehensive member onboarding!**

New members will be guided through a complete profile setup process, creating a rich database of team member information for better collaboration and community building.