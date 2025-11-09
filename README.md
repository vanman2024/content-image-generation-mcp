# Content & Image Generation MCP Server

AI-powered content and image generation FastMCP server with Google Imagen 3/4 image generation, Veo 2/3 video generation, and Claude/Gemini content generation.

**Production Ready**: Deploy to FastMCP Cloud in 5 minutes!

[![Deploy to FastMCP Cloud](https://img.shields.io/badge/Deploy-FastMCP%20Cloud-blue)](https://cloud.fastmcp.com)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13.0+-green.svg)](https://gofastmcp.com)

## Quick Links

- **[5-Minute Deployment Guide](./docs/deployment/QUICK_START.md)** - Get started fast
- **[Complete Deployment Guide](./docs/deployment/FASTMCP_CLOUD_DEPLOYMENT.md)** - Detailed instructions
- **[Deployment Checklist](./docs/deployment/DEPLOYMENT_CHECKLIST.md)** - Ensure nothing is missed

## Features

### Tools

1. **health_check** - Server health and monitoring
   - Verify server health and API connectivity
   - Check service availability (Google AI, Anthropic)
   - Output directory validation
   - Perfect for monitoring deployments

2. **generate_image_imagen3** - Generate high-quality marketing images
   - Google Imagen 3/4 integration
   - Multiple aspect ratios (1:1, 16:9, 9:16, 4:3, 3:4)
   - 1K and 2K resolution options
   - Negative prompts for better control
   - Production-ready with error handling

3. **batch_generate_images** - Generate multiple images efficiently
   - Batch processing for campaigns
   - Cost tracking across multiple images
   - Consistent quality and style
   - Detailed success/failure reporting

4. **generate_video_veo3** - Create marketing videos
   - Google Veo 3 integration
   - Customizable duration (4, 6, 8 seconds)
   - 720p and 1080p resolution
   - Native audio generation
   - Cost estimation per second

5. **generate_marketing_content** - AI-powered copywriting
   - Multiple content types (social posts, blog intros, ad copy, email subjects, product descriptions)
   - Choice of Claude Sonnet 4 or Gemini 2.5 Flash Image
   - Tone customization (professional, casual, enthusiastic, formal)
   - Length control (short, medium, long)
   - Optional hashtag generation

6. **calculate_cost_estimate** - Campaign budget planning
   - Detailed cost breakdown by service
   - Support for multiple models
   - Per-resource pricing
   - Campaign planning assistant

### Resources

- **config://pricing** - Current pricing for all services
- **config://models** - Available AI models and capabilities

### Prompts

- **campaign_planner** - Interactive campaign planning assistant
- **image_prompt_enhancer** - Optimize image generation prompts

## Prerequisites

- **Python 3.10+** (required for FastMCP)
- **uv** or **pip** package manager
- **Google Cloud Account** with Vertex AI API enabled
- **Anthropic API Key** (for Claude content generation)
- **Google AI API Key** (for Gemini content generation)

## Installation

### 1. Clone or Navigate to Project

```bash
cd marketing-automation
```

### 2. Create Virtual Environment

Using `uv` (recommended):
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Or using standard Python:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

Using `uv`:
```bash
uv pip install -e .
```

Or using pip:
```bash
pip install -e .
```

For development with testing tools:
```bash
uv pip install -e ".[dev]"
```

## Configuration

### 1. Set Up Google Cloud

1. Create a Google Cloud project at https://console.cloud.google.com
2. Enable the Vertex AI API
3. Create a service account with Vertex AI permissions
4. Download the service account key JSON file
5. Set the path to your credentials file

### 2. Get API Keys

- **Anthropic**: Get your API key from https://console.anthropic.com
- **Google AI**: Get your API key from https://makersuite.google.com/app/apikey

### 3. Create Environment File

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Anthropic API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Google Generative AI (Gemini)
GOOGLE_API_KEY=your-google-ai-api-key

# Server Configuration
MCP_SERVER_NAME=Marketing Automation
MCP_SERVER_PORT=8000
```

**Important**: Never commit the `.env` file with real credentials!

## Usage

### Local Development (STDIO for Claude Desktop)

Run the server in STDIO mode:
```bash
python server.py
```

Or using FastMCP CLI:
```bash
fastmcp run server.py
```

### HTTP Server for Deployment

Run the server in HTTP mode:
```bash
python server.py --http
```

The server will start on `http://0.0.0.0:8000`

### Claude Desktop Integration

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "marketing-automation": {
      "command": "python",
      "args": [
        "/absolute/path/to/marketing-automation/server.py"
      ],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-project-id",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account-key.json",
        "ANTHROPIC_API_KEY": "sk-ant-api03-your-key",
        "GOOGLE_API_KEY": "your-google-ai-key"
      }
    }
  }
}
```

**Note**: Use absolute paths for both the server script and credentials file.

## Example Usage

### Generate a Marketing Image

```python
# Via Claude Desktop or MCP client
generate_image_imagen3(
    prompt="Professional product photography of a luxury watch, white background, studio lighting, high detail, commercial quality",
    aspect_ratio="1:1",
    quality="hd"
)
```

### Batch Generate Images for Campaign

```python
batch_generate_images(
    prompts=[
        "Modern tech startup office, collaborative workspace, natural light",
        "Smartphone app interface, clean design, user-friendly",
        "Happy customers using product, lifestyle photography"
    ],
    quality="hd",
    aspect_ratio="16:9"
)
```

### Generate Marketing Copy

```python
generate_marketing_content(
    content_type="social_post",
    topic="Launch of new AI-powered analytics platform",
    tone="enthusiastic",
    length="medium",
    model="claude",
    include_hashtags=True
)
```

### Estimate Campaign Costs

```python
calculate_cost_estimate(
    images_hd=10,
    images_sd=20,
    video_seconds=30,
    content_pieces=15
)
```

## Pricing

Approximate costs (as of October 2025):

| Service | Cost |
|---------|------|
| Imagen 3 SD | $0.020 per image |
| Imagen 3 HD | $0.040 per image |
| Imagen 4 SD | $0.025 per image |
| Imagen 4 HD | $0.050 per image |
| Veo 2 | $0.15 per second |
| Veo 3 | $0.20 per second |
| Claude Sonnet | $0.003 per 1K tokens |
| Gemini Pro | $0.0005 per 1K tokens |

Use `calculate_cost_estimate` tool for detailed budget planning.

## Output Directory

Generated content is saved to the `output/` directory:
- Images: `output/imagen3_YYYYMMDD_HHMMSS.png`
- Videos: `output/veo3_YYYYMMDD_HHMMSS.mp4`

## Security Best Practices

1. **Never hardcode API keys** - Always use environment variables
2. **Use .env for local development** - Never commit `.env` to git
3. **Rotate credentials regularly** - Especially for production use
4. **Set up cost alerts** - Monitor Google Cloud and Anthropic usage
5. **Use service accounts with minimal permissions** - Follow principle of least privilege

## Deployment

### FastMCP Cloud (Recommended)

**Quick Deployment**: Deploy to production in 5 minutes!

1. **Visit**: https://cloud.fastmcp.com
2. **Sign in with GitHub**
3. **Create new project**:
   - Repository: `vanman2024/content-image-generation-mcp`
   - Entrypoint: `server.py:mcp`
4. **Set environment variable**: `GOOGLE_API_KEY=<your-key>`
5. **Deploy**

Your server will be available at:
```
https://content-image-generation-mcp.fastmcp.app/mcp
```

**Full Documentation**:
- [Quick Start Guide](./docs/deployment/QUICK_START.md) - 5-minute deployment
- [Complete Deployment Guide](./docs/deployment/FASTMCP_CLOUD_DEPLOYMENT.md) - Detailed instructions
- [Deployment Checklist](./docs/deployment/DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist

**Validation** (optional but recommended):
```bash
./scripts/validate-deployment.sh
```

### Production Features

Your deployment includes:
- ✅ Structured logging with configurable levels
- ✅ Health check endpoint for monitoring
- ✅ Error handling and API validation
- ✅ Automatic redeployment on git push
- ✅ Zero-downtime deployments
- ✅ Cost tracking and estimation

### IDE Integration

After deploying, connect from your IDE:

**Claude Desktop** (`claude_desktop_config.json`):
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

**Cursor** (`.cursor/mcp_config.json`):
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

### Alternative Deployment Options

**Local Development (STDIO)**:
```bash
python server.py
# or
fastmcp run server.py
```

**HTTP Server**:
```bash
python server.py --http
# Server runs on http://0.0.0.0:8000
```

**Docker**:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV GOOGLE_API_KEY=""
CMD ["python", "server.py", "--http"]
```

Build and run:
```bash
docker build -t content-image-generation-mcp .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key content-image-generation-mcp
```

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
uv pip install --force-reinstall -e .
```

### Google Cloud Authentication

```bash
# Verify credentials
gcloud auth application-default login

# Check project
gcloud config get-value project
```

### API Key Issues

```bash
# Verify environment variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black server.py
ruff check server.py
```

### Add New Tools

Follow FastMCP patterns:

```python
@mcp.tool()
def my_new_tool(param: str) -> Dict[str, Any]:
    """Tool description for LLM"""
    return {"success": True, "result": param}
```

## Resources

- **FastMCP Documentation**: https://gofastmcp.com
- **Google Vertex AI**: https://cloud.google.com/vertex-ai/docs
- **Anthropic Claude**: https://docs.anthropic.com
- **Google Gemini**: https://ai.google.dev

## Support

For issues or questions:
1. Check the FastMCP documentation
2. Review Google Cloud Vertex AI docs
3. Verify API credentials and quotas
4. Check the `output/` directory for generated files

## License

Apache 2.0

---

**Built with FastMCP 2.13.0** - The fast, Pythonic way to build MCP servers.
