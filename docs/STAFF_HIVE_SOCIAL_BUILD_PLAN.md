# Staff Hive Social - Build Plan Using Claude Agent SDK Commands

**Project:** Social Media Campaign Orchestrator (Staff Hive Social)
**Purpose:** Multi-brand AI-powered social media management system
**Stack:** TypeScript Agent SDK + MCP Servers + REST APIs

---

## Summary of Previous Discussion

### What We Built
1. ✅ **content-image-generation-mcp** - AI content and image generation (FastMCP, deployed)
2. ✅ **logo-overlay-service** - Brand logo overlay (FastAPI, ready to deploy)
3. ✅ **Airtable structure** - Brands, Content Pieces, Assets, Social Media Posts Queue

### What We Need to Build
**Agent SDK Orchestrator** - TypeScript application that:
- Queries Airtable for brand context (REST API)
- Calls content-image-generation MCP for AI content/images
- Calls logo-overlay service for branding
- Stores results back in Airtable
- Exposes HTTP endpoint for triggering (Airtable automation/Make.com)

### Key Architecture Decisions
- **TypeScript** for Agent SDK app (not Python)
- **No Airtable MCP** (use REST API directly - stdio MCP not production-ready)
- **HTTP-based services** only (all deployable)
- **Airtable as trigger** (automation when Status = "Pending")

---

## Available Claude Agent SDK Slash Commands

### Core Setup Commands

#### 1. `/claude-agent-sdk:new-app`
**Purpose:** Initialize new Agent SDK TypeScript application
**When to use:** First step - creates project structure

**What it does:**
- Creates `package.json` with Agent SDK dependencies
- Sets up TypeScript configuration
- Creates basic project structure
- Initializes git repository

**Usage for this project:**
```bash
/claude-agent-sdk:new-app "staff-hive-social" "Social media campaign orchestrator for multi-brand management"
```

---

#### 2. `/claude-agent-sdk:add-custom-tools`
**Purpose:** Add custom tool definitions for external APIs
**When to use:** After project setup - for Airtable API and logo service

**What it does:**
- Creates `src/tools/` directory
- Generates tool definition templates
- Adds Zod schema validation
- Integrates with Agent SDK query options

**Tools we need to create:**
1. **Airtable Tools:**
   - `query_brand` - Get brand from Airtable Brands table
   - `create_content_piece` - Store generated content
   - `create_asset` - Store generated images
   - `create_social_post` - Create queue record

2. **Logo Service Tool:**
   - `overlay_logo` - Add brand logo to image

**Usage:**
```bash
/claude-agent-sdk:add-custom-tools
# Then specify: query_brand, create_content_piece, create_asset, create_social_post, overlay_logo
```

---

#### 3. `/claude-agent-sdk:add-mcp`
**Purpose:** Configure MCP server connections
**When to use:** For content-image-generation MCP integration

**What it does:**
- Configures MCP server connections in options
- Sets up HTTP/SSE/stdio transport
- Handles authentication/environment variables

**For this project:**
```typescript
mcpServers: {
  "content-gen": {
    type: "http",
    url: "https://content.fastmcp.app/mcp"
  }
}
```

**Usage:**
```bash
/claude-agent-sdk:add-mcp
# Configure: content-gen MCP with HTTP transport
```

---

#### 4. `/claude-agent-sdk:add-subagents`
**Purpose:** Create specialized sub-agents for different tasks
**When to use:** For modular workflow components

**Subagents we could create:**
1. **Brand Context Agent** - Queries Airtable, builds enhanced prompts
2. **Content Generator Agent** - Calls MCP for AI content
3. **Image Processor Agent** - Calls MCP for images, adds logos
4. **Storage Agent** - Stores results in Airtable

**What it does:**
- Creates `.claude/agents/` directory
- Generates subagent markdown files
- Defines specialized prompts and tool access

**Usage:**
```bash
/claude-agent-sdk:add-subagents
# Create: brand-context-agent, content-generator-agent, image-processor-agent, storage-agent
```

---

#### 5. `/claude-agent-sdk:add-system-prompts`
**Purpose:** Define agent behavior and workflow
**When to use:** Core orchestration logic

**What it does:**
- Sets up system prompt configuration
- Defines agent role and responsibilities
- Specifies workflow steps

**For this project:**
```
You are a social media campaign orchestrator.

WORKFLOW:
1. Query Airtable for brand context
2. Build enhanced campaign brief with brand data
3. Call content-image-generation MCP for AI content/images
4. Call logo-overlay service to add brand logos
5. Store all results in Airtable
6. Return campaign summary

TOOLS AVAILABLE:
- query_brand, create_content_piece, create_asset, create_social_post
- overlay_logo
- content-gen MCP (batch_generate_campaign)
```

**Usage:**
```bash
/claude-agent-sdk:add-system-prompts
# Define orchestrator workflow
```

---

#### 6. `/claude-agent-sdk:add-slash-commands`
**Purpose:** Add user-facing commands (like /campaign:generate)
**When to use:** For command-line interface to the orchestrator

**Slash commands we could create:**
- `/campaign:generate` - Generate new campaign
- `/campaign:review` - Review generated content before posting
- `/campaign:publish` - Approve and post to social media
- `/brand:add` - Add new brand to Airtable
- `/analytics:report` - Generate performance report

**What it does:**
- Creates command definitions in `.claude/commands/`
- Maps commands to agent workflows
- Handles parameter parsing

**Usage:**
```bash
/claude-agent-sdk:add-slash-commands
# Create: campaign:generate, campaign:review, campaign:publish
```

---

#### 7. `/claude-agent-sdk:add-skills`
**Purpose:** Create reusable agent capabilities
**When to use:** For common operations used across workflows

**Skills we could create:**
1. **brand-context-extraction** - Pull brand data from Airtable
2. **prompt-enhancement** - Build enhanced prompts with brand context
3. **multi-platform-optimization** - Validate content for platform constraints
4. **content-validation** - Check character limits, hashtag counts

**What it does:**
- Creates `.claude/skills/` directory
- Generates skill markdown templates
- Makes skills available to agents

**Usage:**
```bash
/claude-agent-sdk:add-skills
# Create: brand-context-extraction, prompt-enhancement, multi-platform-optimization
```

---

### Production-Ready Commands

#### 8. `/claude-agent-sdk:add-hosting`
**Purpose:** Configure deployment settings
**When to use:** Before deploying to Railway/DigitalOcean

**What it does:**
- Generates Dockerfile
- Creates deployment configs
- Sets up environment variables
- Configures health checks

**Usage:**
```bash
/claude-agent-sdk:add-hosting
# Target: Railway (or DigitalOcean)
```

---

#### 9. `/claude-agent-sdk:add-streaming`
**Purpose:** Enable real-time response streaming
**When to use:** For long-running campaign generation

**What it does:**
- Configures streaming responses
- Sets up SSE or WebSocket
- Handles partial message updates

**Usage:**
```bash
/claude-agent-sdk:add-streaming
# For real-time campaign generation progress
```

---

#### 10. `/claude-agent-sdk:add-sessions`
**Purpose:** Manage user sessions and conversation state
**When to use:** For multi-turn conversations or review workflows

**What it does:**
- Implements session storage
- Handles conversation history
- Manages state persistence

**Usage:**
```bash
/claude-agent-sdk:add-sessions
# For campaign review and iteration
```

---

#### 11. `/claude-agent-sdk:add-permissions`
**Purpose:** Control tool access and authorization
**When to use:** For security and access control

**What it does:**
- Configures tool permissions
- Sets up authorization rules
- Manages allowed/disallowed operations

**Usage:**
```bash
/claude-agent-sdk:add-permissions
# Restrict certain operations based on user/context
```

---

#### 12. `/claude-agent-sdk:add-cost-tracking`
**Purpose:** Monitor API usage and costs
**When to use:** Track Imagen/Gemini API costs per campaign

**What it does:**
- Tracks token usage
- Monitors API costs
- Generates cost reports

**Usage:**
```bash
/claude-agent-sdk:add-cost-tracking
# Track costs per campaign/brand
```

---

#### 13. `/claude-agent-sdk:add-todo-tracking`
**Purpose:** Manage workflow tasks
**When to use:** For campaign generation progress tracking

**What it does:**
- Creates todo list management
- Tracks task completion
- Shows progress status

**Usage:**
```bash
/claude-agent-sdk:add-todo-tracking
# Track: Brand query, Content gen, Image gen, Logo overlay, Storage
```

---

#### 14. `/claude-agent-sdk:add-plugins`
**Purpose:** Load custom plugins
**When to use:** For extending functionality

**What it does:**
- Configures plugin loading
- Integrates external plugins
- Manages plugin dependencies

**Usage:**
```bash
/claude-agent-sdk:add-plugins
# If we build custom plugins for social media features
```

---

## Recommended Build Sequence

### Phase 1: Project Setup (Day 1)

```bash
# 1. Create new project
/claude-agent-sdk:new-app "staff-hive-social" "Social media campaign orchestrator"

# 2. Add MCP server connection
/claude-agent-sdk:add-mcp
# Configure: content-gen HTTP MCP

# 3. Add custom tools
/claude-agent-sdk:add-custom-tools
# Create: query_brand, create_content_piece, create_asset, overlay_logo

# 4. Add system prompts
/claude-agent-sdk:add-system-prompts
# Define: Campaign orchestrator workflow
```

### Phase 2: Core Features (Day 1-2)

```bash
# 5. Add subagents (optional - for modular design)
/claude-agent-sdk:add-subagents
# Create: brand-context-agent, content-generator-agent, image-processor-agent

# 6. Add skills (reusable logic)
/claude-agent-sdk:add-skills
# Create: brand-context-extraction, prompt-enhancement, content-validation

# 7. Add slash commands
/claude-agent-sdk:add-slash-commands
# Create: campaign:generate, campaign:review
```

### Phase 3: Production Features (Day 2-3)

```bash
# 8. Add cost tracking
/claude-agent-sdk:add-cost-tracking

# 9. Add todo tracking
/claude-agent-sdk:add-todo-tracking

# 10. Add streaming (for real-time updates)
/claude-agent-sdk:add-streaming

# 11. Add hosting configuration
/claude-agent-sdk:add-hosting
# Target: Railway
```

### Phase 4: Testing & Deployment (Day 3)

```bash
# 12. Test skill loading
/claude-agent-sdk:test-skill-loading

# 13. Deploy to Railway
# (Manual: railway init && railway up)

# 14. Configure Airtable automation to call HTTP endpoint
```

---

## Project File Structure (After Commands)

```
staff-hive-social/
├── package.json                    # From: /new-app
├── tsconfig.json                   # From: /new-app
├── .env.example                    # From: /new-app
├── src/
│   ├── index.ts                   # Main entry point
│   ├── tools/                     # From: /add-custom-tools
│   │   ├── airtable.ts           # Airtable REST API tools
│   │   ├── logo-overlay.ts       # Logo service tool
│   │   └── index.ts
│   ├── config/
│   │   ├── mcp.ts                # From: /add-mcp
│   │   └── system-prompts.ts     # From: /add-system-prompts
│   └── utils/
│       ├── cost-tracking.ts      # From: /add-cost-tracking
│       └── streaming.ts          # From: /add-streaming
├── .claude/
│   ├── agents/                   # From: /add-subagents
│   │   ├── brand-context-agent.md
│   │   ├── content-generator-agent.md
│   │   └── image-processor-agent.md
│   ├── skills/                   # From: /add-skills
│   │   ├── brand-context-extraction.md
│   │   ├── prompt-enhancement.md
│   │   └── content-validation.md
│   └── commands/                 # From: /add-slash-commands
│       ├── campaign-generate.md
│       └── campaign-review.md
├── Dockerfile                    # From: /add-hosting
├── railway.json                  # From: /add-hosting
└── README.md

```

---

## Environment Variables Needed

```bash
# .env
ANTHROPIC_API_KEY=your_key_here
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=apprJV9UhYEDNL6J7
LOGO_SERVICE_URL=http://logo-overlay-service:8001
CONTENT_MCP_URL=https://content.fastmcp.app/mcp
```

---

## Custom Tools Details

### Tool 1: query_brand
```typescript
// src/tools/airtable.ts
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

export const queryBrand = tool(
  "query_brand",
  "Get brand information from Airtable Brands table",
  {
    brand_name: z.string().describe("Brand name to query")
  },
  async ({ brand_name }) => {
    const response = await fetch(
      `https://api.airtable.com/v0/${process.env.AIRTABLE_BASE_ID}/Brands?filterByFormula={Brand Name}='${brand_name}'`,
      {
        headers: {
          'Authorization': `Bearer ${process.env.AIRTABLE_API_KEY}`
        }
      }
    );

    const data = await response.json();
    if (!data.records || data.records.length === 0) {
      throw new Error(`Brand "${brand_name}" not found in Airtable`);
    }

    return data.records[0].fields;
  }
);
```

### Tool 2: create_content_piece
```typescript
export const createContentPiece = tool(
  "create_content_piece",
  "Store generated content in Airtable Content Pieces table",
  {
    campaign_brief: z.string(),
    platform: z.string(),
    content: z.string(),
    hashtags: z.string(),
    brand_id: z.string()
  },
  async (args) => {
    const response = await fetch(
      `https://api.airtable.com/v0/${process.env.AIRTABLE_BASE_ID}/Content%20Pieces`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.AIRTABLE_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          fields: {
            "Campaign Brief": args.campaign_brief,
            "Platform": args.platform,
            "Generated Content": args.content,
            "Generated Hashtags": args.hashtags,
            "Brand": [args.brand_id],
            "Content Status": "Ready"
          }
        })
      }
    );

    return await response.json();
  }
);
```

### Tool 3: overlay_logo
```typescript
// src/tools/logo-overlay.ts
import { tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

export const overlayLogo = tool(
  "overlay_logo",
  "Add brand logo to generated image",
  {
    base_image_base64: z.string(),
    brand_name: z.string(),
    position: z.enum(["top-left", "top-right", "bottom-left", "bottom-right"]).optional()
  },
  async (args) => {
    const response = await fetch(
      `${process.env.LOGO_SERVICE_URL}/overlay-logo`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_image_base64: args.base_image_base64,
          brand_name: args.brand_name,
          position: args.position || "bottom-right",
          logo_width: 200,
          logo_height: 200,
          opacity: 0.85
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Logo overlay failed: ${response.statusText}`);
    }

    return await response.json();
  }
);
```

---

## Next Steps for Building

1. **Review this plan** - Make sure approach is correct
2. **Run slash commands in sequence** - Use the build sequence above
3. **Test locally** - Verify each component works
4. **Deploy services:**
   - Logo overlay service → Railway
   - Agent SDK app → Railway
5. **Configure Airtable automation** - Trigger on Status = "Pending"
6. **Test end-to-end** - Generate first campaign

---

## Questions to Resolve Before Building

1. **Logo service deployment** - Deploy to Railway first?
2. **Airtable table IDs** - Need exact IDs for Content Pieces, Assets, etc.
3. **Testing strategy** - Manual via slash commands or automated tests?
4. **Error handling** - What happens if MCP server fails?
5. **Cost limits** - Set maximum cost per campaign?

---

## Summary

This document provides a complete build plan using Claude Agent SDK slash commands. The approach:
- Uses TypeScript Agent SDK (not Python)
- Calls Airtable REST API directly (no stdio MCP)
- Integrates content-image-generation MCP (HTTP)
- Calls logo-overlay service (HTTP)
- Orchestrates complete workflow autonomously
- Deploys as HTTP service callable from Airtable/Make.com

**Ready to start building when you are!**
