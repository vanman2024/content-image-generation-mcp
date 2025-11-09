# FastMCP Cloud Deployment Checklist

Use this checklist to ensure successful deployment of the Content & Image Generation MCP Server.

---

## Pre-Deployment Checklist

### Code Quality & Configuration

- [ ] Server file (`server.py`) exists and is valid Python
- [ ] No syntax errors in server code
- [ ] `fastmcp.json` configuration is valid JSON
- [ ] `requirements.txt` includes all dependencies
- [ ] FastMCP dependency declared: `fastmcp>=2.13.0`
- [ ] Google Gen AI dependency declared: `google-genai>=1.0.0`
- [ ] Dependencies have version constraints
- [ ] `.env.example` documents all environment variables
- [ ] No hardcoded API keys in code
- [ ] `.gitignore` excludes `.env` files

### Repository Status

- [ ] All changes committed to git
- [ ] Working directory is clean (`git status`)
- [ ] Pushed to GitHub repository
- [ ] Repository URL: `https://github.com/vanman2024/content-image-generation-mcp`
- [ ] Main branch is up to date

### Environment Configuration

- [ ] `.env.example` has all required variables
- [ ] Required: `GOOGLE_API_KEY` documented
- [ ] Optional: `ANTHROPIC_API_KEY` documented
- [ ] Optional: `LOG_LEVEL` documented
- [ ] All variables have placeholder values (not real keys)

### Testing

- [ ] Server runs locally without errors
- [ ] Health check tool works
- [ ] Image generation tested locally
- [ ] Content generation tested locally
- [ ] No runtime errors in logs

---

## FastMCP Cloud Setup Checklist

### Account & Authentication

- [ ] FastMCP Cloud account created at https://cloud.fastmcp.com
- [ ] GitHub account connected
- [ ] Repository access granted to FastMCP Cloud
- [ ] Organization permissions confirmed (if applicable)

### Project Creation

- [ ] Clicked "New Project" in FastMCP Cloud dashboard
- [ ] Selected repository: `vanman2024/content-image-generation-mcp`
- [ ] Selected branch: `main`
- [ ] Set project name: `content-image-generation-mcp`
- [ ] Set authentication: Organization-only or Public

### Server Entrypoint Configuration

- [ ] **CRITICAL**: Entrypoint set to: `server.py:mcp`
- [ ] Verified entrypoint format: `<file>:<object>`
- [ ] Confirmed `mcp` is the FastMCP instance name in `server.py`

### Environment Variables

- [ ] Navigated to Environment Variables section
- [ ] Added `GOOGLE_API_KEY` with real API key
- [ ] Verified Google AI API key is valid (from https://aistudio.google.com/apikey)
- [ ] (Optional) Added `ANTHROPIC_API_KEY` if using Claude
- [ ] (Optional) Set `LOG_LEVEL` to `INFO` or `WARNING`
- [ ] Double-checked all variable names match `.env.example`
- [ ] No typos in variable names (case-sensitive!)

---

## Deployment Checklist

### Initiate Deployment

- [ ] Clicked "Deploy" button in FastMCP Cloud
- [ ] Deployment started successfully
- [ ] Build logs are visible

### Monitor Deployment

- [ ] Watched deployment progress (2-5 minutes expected)
- [ ] Checked for dependency installation errors
- [ ] Verified Python version detected correctly (>=3.10)
- [ ] Confirmed all dependencies installed successfully
- [ ] Deployment status changed to "Active"

### Deployment URL

- [ ] Deployment URL generated
- [ ] URL format: `https://content-image-generation-mcp.fastmcp.app/mcp`
- [ ] Copied URL for later use

---

## Post-Deployment Verification Checklist

### Basic Connectivity

- [ ] Server shows "Active" status in dashboard
- [ ] Deployment logs show no errors
- [ ] Server startup message visible in logs
- [ ] No Python exceptions in logs

### Service Initialization

Check logs for these messages:
- [ ] `"Starting Content & Image Generation server"`
- [ ] `"Google Gen AI client initialized successfully"`
- [ ] (Optional) `"Anthropic client initialized successfully"`

### Health Check

- [ ] Connected to server from IDE/client
- [ ] Executed `health_check` tool
- [ ] Health status shows `"healthy"`
- [ ] `google_genai` service shows `true`
- [ ] Output directory is writable

### Tool Testing

- [ ] Listed available tools (should show 7 tools)
- [ ] Tested `generate_image_imagen3` with simple prompt
- [ ] Image generated successfully
- [ ] Cost calculated correctly
- [ ] Tested `generate_marketing_content` with topic
- [ ] Content generated successfully
- [ ] No errors in logs

---

## IDE Integration Checklist

### Claude Desktop

- [ ] Located `claude_desktop_config.json`
- [ ] Added server configuration:
  ```json
  {
    "content-image-generation": {
      "url": "https://content-image-generation-mcp.fastmcp.app/mcp",
      "transport": "sse"
    }
  }
  ```
- [ ] Restarted Claude Desktop
- [ ] Server appears in available servers list
- [ ] Successfully called a tool

### Cursor

- [ ] Located `.cursor/mcp_config.json`
- [ ] Added server configuration:
  ```json
  {
    "content-image-generation": {
      "url": "https://content-image-generation-mcp.fastmcp.app/mcp",
      "transport": "sse"
    }
  }
  ```
- [ ] Restarted Cursor
- [ ] Server appears in MCP servers list
- [ ] Successfully called a tool

### Claude Code

- [ ] Located `.claude/mcp.json`
- [ ] Added server configuration:
  ```json
  {
    "content-image-generation": {
      "url": "https://content-image-generation-mcp.fastmcp.app/mcp",
      "transport": "http"
    }
  }
  ```
- [ ] Restarted Claude Code
- [ ] Server appears in available servers
- [ ] Successfully called a tool

---

## Documentation Checklist

### Deployment Records

- [ ] Updated `.fastmcp-deployments.json` with:
  - Deployment ID
  - Timestamp
  - Environment variables used
  - Deployment URL
  - Git commit hash
  - Version number

### Team Documentation

- [ ] Shared deployment URL with team
- [ ] Documented environment variable setup
- [ ] Created usage guide for team members
- [ ] Added IDE integration instructions
- [ ] Documented available tools and their costs

---

## Monitoring Setup Checklist

### FastMCP Cloud Dashboard

- [ ] Bookmarked project dashboard URL
- [ ] Enabled email notifications for deployment failures
- [ ] Set up log monitoring for errors
- [ ] Configured performance alerts (if available)

### Cost Monitoring

- [ ] Reviewed pricing information
- [ ] Set `COST_ALERT_THRESHOLD` if needed
- [ ] Planned regular usage review schedule
- [ ] Documented cost estimation process for team

---

## Security Checklist

### API Keys

- [ ] API keys stored only in FastMCP Cloud environment variables
- [ ] No API keys in git repository
- [ ] No API keys in deployment logs
- [ ] `.env` file is gitignored
- [ ] API keys are valid and not expired

### Access Control

- [ ] Repository access limited to authorized users
- [ ] FastMCP Cloud project access restricted
- [ ] Authentication mode configured (public vs organization-only)
- [ ] Reviewed who has deployment access

---

## Troubleshooting Checklist

If deployment fails, check:

- [ ] FastMCP Cloud deployment logs for errors
- [ ] Environment variables are set correctly
- [ ] API keys are valid
- [ ] Repository contains all required files
- [ ] `requirements.txt` dependencies are compatible
- [ ] Server entrypoint is correct: `server.py:mcp`
- [ ] Python version is 3.10+

If server is unhealthy:

- [ ] Run `health_check` tool to diagnose
- [ ] Check FastMCP Cloud logs for errors
- [ ] Verify Google API key validity
- [ ] Check output directory permissions
- [ ] Review startup logs for initialization errors

---

## Maintenance Checklist

### Regular Tasks

- [ ] Weekly: Review deployment logs for errors
- [ ] Weekly: Check API usage and costs
- [ ] Monthly: Review and rotate API keys
- [ ] Monthly: Update dependencies if needed
- [ ] Quarterly: Review security settings

### Updates

When updating server code:
- [ ] Test changes locally first
- [ ] Update version in `fastmcp.json`
- [ ] Commit and push to GitHub
- [ ] Monitor automatic redeployment
- [ ] Verify new version is working
- [ ] Update team documentation if needed

---

## Success Criteria

Deployment is successful when:

- ✅ Server status is "Active" in FastMCP Cloud
- ✅ No errors in deployment logs
- ✅ Health check returns "healthy"
- ✅ All tools are callable and working
- ✅ Image generation completes successfully
- ✅ Content generation completes successfully
- ✅ Cost calculation is accurate
- ✅ IDE integration works
- ✅ Team can access and use the server
- ✅ Documentation is complete and shared

---

## Post-Deployment Next Steps

- [ ] Create usage examples for common workflows
- [ ] Train team on available tools
- [ ] Set up regular cost review meetings
- [ ] Plan for feature enhancements
- [ ] Schedule security review
- [ ] Gather user feedback

---

**Checklist Version**: 1.0.0
**Last Updated**: 2025-11-09
