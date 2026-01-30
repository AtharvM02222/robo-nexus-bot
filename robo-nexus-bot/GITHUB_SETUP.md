# GitHub Integration Setup

## Optional: GitHub Token for Advanced Features

To enable automatic commit notifications and issue creation, you can add a GitHub token:

### 1. Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Robo Nexus Bot"
4. Select scopes:
   - `repo` (for private repos) or `public_repo` (for public repos only)
   - `issues` (to create issues)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### 2. Add Token to Replit

1. In your Replit project, go to the "Secrets" tab (🔒 icon)
2. Add a new secret:
   - Key: `GITHUB_TOKEN`
   - Value: Your GitHub token
3. The bot will automatically use this token when available

### 3. Features Enabled with Token

**With GitHub Token:**
- ✅ Automatic commit notifications every 5 minutes
- ✅ Create GitHub issues from Discord (`/create_issue`)
- ✅ Enhanced repository statistics

**Without GitHub Token:**
- ✅ View recent commits (`/recent_commits`)
- ✅ Repository statistics (`/repo_stats`)
- ❌ No automatic commit notifications
- ❌ Cannot create issues from Discord

### 4. Commands Available

- `/recent_commits` - Show recent commits (works without token)
- `/repo_stats` - Repository statistics (works without token)
- `/create_issue` - Create GitHub issue (requires token)

The bot will work perfectly fine without a GitHub token - you just won't get automatic commit notifications!