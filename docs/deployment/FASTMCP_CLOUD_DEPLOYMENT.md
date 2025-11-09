# FastMCP Cloud Deployment Guide

Complete guide for deploying the Content & Image Generation MCP Server to FastMCP Cloud.

## Quick Reference

**GitHub Repository**: https://github.com/vanman2024/content-image-generation-mcp
**Server Entrypoint**: `server.py:mcp`
**Expected Deployment URL**: `https://content-image-generation-mcp.fastmcp.app/mcp`

---

## Prerequisites

1. **GitHub Account**: Required for repository connection
2. **FastMCP Cloud Account**: Sign up at https://cloud.fastmcp.com
3. **Google AI API Key**: Get from https://aistudio.google.com/apikey
4. **Repository Access**: Ensure your GitHub account has access to the repository

---

## Step 1: Verify Repository

Your server is already connected to GitHub:
```
Repository: https://github.com/vanman2024/content-image-generation-mcp
Branch: main
```

The repository includes:
- ✅ `server.py` - Main FastMCP server file
- ✅ `requirements.txt` - Python dependencies
- ✅ `fastmcp.json` - Server configuration
- ✅ `.env.example` - Environment variable template
- ✅ Production logging and error handling
- ✅ Health check endpoint

---

## Step 2: FastMCP Cloud Configuration

### Visit FastMCP Cloud Dashboard

1. Navigate to: **https://cloud.fastmcp.com**
2. Click **"Sign in with GitHub"**
3. Authorize FastMCP Cloud access to your repositories

### Create New Project

1. Click **"New Project"**
2. Select repository: **`vanman2024/content-image-generation-mcp`**
3. Configure project settings:

```yaml
Project Name: content-image-generation-mcp
Repository: vanman2024/content-image-generation-mcp
Branch: main
Entrypoint: server.py:mcp
Authentication: Private (Organization-only)
```

### Set Server Entrypoint

**CRITICAL**: The entrypoint must be exactly:
```
server.py:mcp
```

This tells FastMCP Cloud:
- **File**: `server.py`
- **Object**: `mcp` (the FastMCP instance in server.py at line 44)

---

## Step 3: Configure Environment Variables

### Required Environment Variable

In the FastMCP Cloud dashboard, add:

| Variable Name | Value | Required |
|--------------|-------|----------|
| `GOOGLE_API_KEY` | `your_google_ai_api_key_here` | ✅ Yes |
| `ANTHROPIC_API_KEY` | `your_anthropic_api_key_here` | ⚠️ Optional |
| `LOG_LEVEL` | `INFO` | ⚠️ Optional |

### How to Get API Keys

**Google AI API Key** (Required):
1. Visit: https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

**Anthropic API Key** (Optional):
1. Visit: https://console.anthropic.com/
2. Sign in or create account
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)

### Environment Variable Configuration in FastMCP Cloud

```
Name: GOOGLE_API_KEY
Value: AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Description: Google AI API for Imagen, Veo, and Gemini

Name: ANTHROPIC_API_KEY (optional)
Value: sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXX
Description: Anthropic API for Claude content generation

Name: LOG_LEVEL (optional)
Value: INFO
Description: Server logging verbosity
```

---

## Step 4: Deploy

1. After configuring environment variables, click **"Deploy"**
2. FastMCP Cloud will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Build the FastMCP server
   - Deploy to unique URL
   - Enable automatic redeployment on git push

### Deployment Process

```
┌─────────────────────────────────────────────┐
│  FastMCP Cloud Deployment Pipeline          │
├─────────────────────────────────────────────┤
│  1. Clone repository from GitHub            │
│  2. Detect Python version (>=3.10)          │
│  3. Install dependencies:                   │
│     - fastmcp>=2.13.0                       │
│     - google-genai>=1.0.0                   │
│     - anthropic>=0.40.0                     │
│     - python-dotenv>=1.0.0                  │
│     - pydantic>=2.0.0                       │
│  4. Load environment variables              │
│  5. Initialize server.py:mcp                │
│  6. Deploy to:                              │
│     https://content-image-generation-mcp    │
│            .fastmcp.app/mcp                 │
│  7. Monitor health and logs                 │
└─────────────────────────────────────────────┘
```

**Expected deployment time**: 2-5 minutes

---

## Step 5: Verify Deployment

### Check Deployment Status

In FastMCP Cloud dashboard:
1. Navigate to your project
2. Check deployment status (should show "Active")
3. View deployment logs for any errors

### Test Health Endpoint

Your deployment URL will be:
```
https://content-image-generation-mcp.fastmcp.app/mcp
```

**Health Check Tool**:
You can test the health check using the `health_check` tool in the MCP server.

### Monitor Logs

FastMCP Cloud provides real-time logs:
1. Go to project dashboard
2. Click "Logs" tab
3. Monitor for:
   - ✅ "Starting Content & Image Generation server"
   - ✅ "Google Gen AI client initialized successfully"
   - ✅ "Anthropic client initialized successfully" (if API key provided)

---

## Step 6: Connect to Your Deployment

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "content-image-generation": {
      "url": "https://content-image-generation-mcp.fastmcp.app/mcp",
      "transport": "sse"
    }
  }
}
```

### Cursor Configuration

Add to `.cursor/mcp_config.json`:
```json
{
  "mcpServers": {
    "content-image-generation": {
      "url": "https://content-image-generation-mcp.fastmcp.app/mcp",
      "transport": "sse"
    }
  }
}
```

### Claude Code Configuration

Add to `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "content-image-generation": {
      "url": "https://content-image-generation-mcp.fastmcp.app/mcp",
      "transport": "http"
    }
  }
}
```

---

## Step 7: Test Your Deployment

### Available Tools

Your deployed server provides:

1. **`health_check`** - Verify server health
2. **`generate_image_imagen3`** - Generate images with Imagen 3/4
3. **`batch_generate_images`** - Generate multiple images
4. **`generate_video_veo3`** - Generate videos with Veo 3
5. **`generate_marketing_content`** - Generate content with Claude/Gemini
6. **`calculate_cost_estimate`** - Estimate campaign costs

### Test Commands

**Test 1: Health Check**
```
Use the health_check tool
```

**Test 2: Generate Image**
```
Use generate_image_imagen3 with:
- prompt: "Professional product photography of a smartphone"
- model_version: "imagen-4.0"
```

**Test 3: Generate Content**
```
Use generate_marketing_content with:
- content_type: "social_post"
- topic: "New product launch"
```

---

## Automatic Redeployment

FastMCP Cloud monitors your `main` branch and automatically redeploys on every push.

### Deployment Workflow

```
┌─────────────────────────────────────────────┐
│  Automatic Redeployment Workflow            │
├─────────────────────────────────────────────┤
│  1. Make changes locally                    │
│  2. Commit and push to GitHub:              │
│     git add .                                │
│     git commit -m "Update server"           │
│     git push origin main                    │
│  3. FastMCP Cloud detects push              │
│  4. Automatic redeployment begins           │
│  5. New version deployed (2-5 minutes)      │
│  6. Old version remains active until ready  │
│  7. Zero-downtime switch to new version     │
└─────────────────────────────────────────────┘
```

---

## Production Features

Your deployed server includes:

### Logging
- ✅ Structured logging with timestamps
- ✅ Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Request/response logging
- ✅ Error tracking with stack traces

### Monitoring
- ✅ Health check endpoint
- ✅ Service availability checks
- ✅ API connectivity verification
- ✅ Output directory validation

### Error Handling
- ✅ Graceful error responses
- ✅ Detailed error messages
- ✅ API key validation
- ✅ Resource availability checks

### Cost Tracking
- ✅ Per-request cost estimation
- ✅ Detailed cost breakdowns
- ✅ Pricing information resource

---

## Troubleshooting

### Common Issues

**Issue 1: "GOOGLE_API_KEY environment variable is required"**
- **Solution**: Verify `GOOGLE_API_KEY` is set in FastMCP Cloud dashboard
- **Check**: Environment Variables section in project settings

**Issue 2: Deployment fails with dependency errors**
- **Solution**: Ensure `requirements.txt` is in repository root
- **Check**: Dependencies are compatible with Python 3.10+

**Issue 3: Server starts but tools don't work**
- **Solution**: Check API key validity at https://aistudio.google.com/apikey
- **Check**: Deployment logs for API authentication errors

**Issue 4: "Server is unhealthy"**
- **Solution**: Use `health_check` tool to diagnose
- **Check**: All services show `true` in health status

### Viewing Logs

1. Go to FastMCP Cloud dashboard
2. Select your project
3. Click "Logs" tab
4. Use search and filter options

### Support

- **FastMCP Cloud**: https://gofastmcp.com/support
- **GitHub Issues**: https://github.com/vanman2024/content-image-generation-mcp/issues
- **Documentation**: https://gofastmcp.com/deployment/fastmcp-cloud

---

## Cost Considerations

### API Usage Costs

Your deployment will incur costs based on usage:

| Service | Cost | Notes |
|---------|------|-------|
| Imagen 3.0 (1K) | $0.02/image | Standard quality |
| Imagen 4.0 (1K) | $0.04/image | Higher quality |
| Imagen 4.0 (2K) | $0.08/image | High resolution |
| Veo 3 | $0.75/second | Video generation |
| Gemini Flash | $0.0005/1K tokens | Content generation |
| Claude Sonnet 4 | $0.003/1K tokens | Content generation |

**Important**: Video generation is expensive! Use cost estimation tool first.

### Cost Management

1. Use `calculate_cost_estimate` before large campaigns
2. Start with Imagen 3.0 for testing
3. Use Gemini instead of Claude for cost savings
4. Set `COST_ALERT_THRESHOLD` environment variable

---

## Security Best Practices

### API Keys
- ✅ Never commit API keys to repository
- ✅ Use FastMCP Cloud environment variables
- ✅ Rotate keys regularly
- ✅ Use separate keys for development/production

### Authentication
- ✅ Enable "Organization-only" access in FastMCP Cloud
- ✅ Restrict repository access to team members
- ✅ Monitor deployment logs for unauthorized access

### Data Protection
- ✅ Generated images/videos stored temporarily
- ✅ No sensitive data logged
- ✅ HTTPS encryption for all API calls

---

## Maintenance

### Updating Dependencies

Update `requirements.txt` and push:
```bash
# Update google-genai
sed -i 's/google-genai>=.*/google-genai>=1.1.0/' requirements.txt
git add requirements.txt
git commit -m "Update google-genai to 1.1.0"
git push origin main
```

FastMCP Cloud will automatically redeploy with new dependencies.

### Monitoring Performance

Check FastMCP Cloud dashboard for:
- Request latency
- Error rates
- API usage
- Deployment uptime

---

## Next Steps

1. ✅ Deploy to FastMCP Cloud
2. ✅ Test all tools
3. ✅ Configure IDE integration
4. ✅ Monitor logs and performance
5. ✅ Set up cost alerts
6. ✅ Create usage documentation for your team

---

**Deployment Date**: 2025-11-09
**Server Version**: 1.0.0
**FastMCP Version**: 2.13.0+
**Python Version**: 3.10+
