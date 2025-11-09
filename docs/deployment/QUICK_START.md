# FastMCP Cloud Deployment - Quick Start

Deploy your Content & Image Generation MCP Server to FastMCP Cloud in 5 minutes.

---

## Prerequisites

- ✅ GitHub account
- ✅ Google AI API Key (get from https://aistudio.google.com/apikey)
- ✅ Repository at https://github.com/vanman2024/content-image-generation-mcp

---

## Deployment Steps

### 1. Validate Server (Optional but Recommended)

Run validation script from server directory:
```bash
cd /home/gotime2022/Projects/mcp-servers/content-media/content-image-generation-mcp
./scripts/validate-deployment.sh
```

Expected output: `✓ Server passed validation - ready for deployment`

### 2. Visit FastMCP Cloud

Go to: **https://cloud.fastmcp.com**

### 3. Sign In

Click **"Sign in with GitHub"**

### 4. Create Project

Click **"New Project"** and configure:

| Setting | Value |
|---------|-------|
| Repository | `vanman2024/content-image-generation-mcp` |
| Branch | `main` |
| Entrypoint | `server.py:mcp` |
| Project Name | `content-image-generation-mcp` |

### 5. Set Environment Variable

Add required environment variable:

```
Name: GOOGLE_API_KEY
Value: <your_google_ai_api_key>
```

**Get your key**: https://aistudio.google.com/apikey

### 6. Deploy

Click **"Deploy"** button

Wait 2-5 minutes for deployment to complete.

### 7. Verify

Your server will be available at:
```
https://content-image-generation-mcp.fastmcp.app/mcp
```

Test with `health_check` tool in your MCP client.

---

## IDE Integration

### Claude Desktop

Edit `claude_desktop_config.json`:
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

Restart Claude Desktop.

### Cursor

Edit `.cursor/mcp_config.json`:
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

Restart Cursor.

---

## Available Tools

Your deployed server provides:

1. **health_check** - Check server health
2. **generate_image_imagen3** - Generate images with Imagen 3/4
3. **batch_generate_images** - Generate multiple images
4. **generate_video_veo3** - Generate videos with Veo 3
5. **generate_marketing_content** - Generate content with AI
6. **calculate_cost_estimate** - Estimate campaign costs

---

## Test Your Deployment

Try generating an image:
```
Use tool: generate_image_imagen3
Prompt: "Professional product photography of a smartphone, centered composition, white background"
Model: imagen-4.0
```

---

## Troubleshooting

**Deployment failed?**
- Check environment variable `GOOGLE_API_KEY` is set
- Verify entrypoint is exactly: `server.py:mcp`
- Review deployment logs in FastMCP Cloud dashboard

**Server unhealthy?**
- Run `health_check` tool
- Check Google API key is valid
- Review server logs

**Tools not working?**
- Verify API key has proper permissions
- Check FastMCP Cloud logs for errors
- Ensure Google AI API is enabled

---

## Next Steps

- ✅ Test all tools
- ✅ Share deployment URL with team
- ✅ Review pricing at `config://pricing`
- ✅ Read full deployment guide: `FASTMCP_CLOUD_DEPLOYMENT.md`
- ✅ Set up cost monitoring

---

## Support

- **Full Guide**: [FASTMCP_CLOUD_DEPLOYMENT.md](./FASTMCP_CLOUD_DEPLOYMENT.md)
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **FastMCP Docs**: https://gofastmcp.com
- **Issues**: https://github.com/vanman2024/content-image-generation-mcp/issues

---

**Quick Start Version**: 1.0.0
**Ready to Deploy**: Yes ✅
