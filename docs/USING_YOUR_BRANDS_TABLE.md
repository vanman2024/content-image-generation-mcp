# Using Your Existing Airtable Brands Table

## The Simple Truth

**This MCP server does NOT need direct Airtable access.**

Your orchestrator (Make.com or separate service) handles the Airtable integration. This keeps things clean and separated.

---

## How It Works (The Right Way)

```
┌─────────────────────────────────────┐
│ Make.com / Orchestrator             │
│                                     │
│ 1. User triggers campaign           │
│ 2. Query Airtable Brands table      │
│ 3. Get brand context                │
│ 4. Build enhanced brief             │
│ 5. Call THIS MCP server             │
└─────────────────────────────────────┘
          ↓ HTTP Request
┌─────────────────────────────────────┐
│ THIS MCP Server                     │
│ content-image-generation-mcp        │
│                                     │
│ Receives enhanced brief with        │
│ brand context already included      │
│                                     │
│ Generates: Content + Images         │
└─────────────────────────────────────┘
```

---

## Example: Challenge Red Seal Campaign

### Step 1: Your Brands Table (Airtable)

```
Brand Name: Challenge Red Seal
Description: Online learning platform for skilled trades professionals
             seeking Red Seal certification. Self-paced courses for
             electricians, plumbers, welders, and other trades.
Target Audience: Apprentices, journey workers, skilled trades professionals
Tone: Professional but approachable, educational, industry-focused
Visual Style: Workshop/training environments, tools, hands-on learning
Color Scheme: #FF0000, #000000, #FFFFFF
```

### Step 2: Make.com Queries Brands Table

```javascript
// Make.com Module: Airtable > Search Records
{
  "base": "apprJV9UhYEDNL6J7",
  "table": "Brands",
  "filterByFormula": "{Brand Name} = 'Challenge Red Seal'"
}

// Returns:
{
  "Brand Name": "Challenge Red Seal",
  "Description": "Online learning platform for...",
  "Target Audience": "Apprentices, journey workers...",
  "Tone": "Professional but approachable..."
}
```

### Step 3: Build Enhanced Campaign Brief

```javascript
// Make.com Module: Set Variable
const brandContext = `
Brand: ${airtable.description}
Target Audience: ${airtable.targetAudience}
Tone: ${airtable.tone}
`;

const campaignTheme = "Promote electrician certification course";

const enhancedBrief = `${campaignTheme}. ${brandContext}`;

// Result:
"Promote electrician certification course.
Brand: Online learning platform for skilled trades professionals seeking
Red Seal certification. Self-paced courses for electricians, plumbers,
welders, and other trades.
Target Audience: Apprentices, journey workers, skilled trades professionals.
Tone: Professional but approachable, educational, industry-focused."
```

### Step 4: Call MCP Server with Enhanced Brief

```javascript
// Make.com Module: HTTP Request
POST https://content.fastmcp.app/mcp
{
  "tool": "batch_generate_campaign",
  "params": {
    "campaign_brief": "Promote electrician certification course. Brand: Online learning platform for skilled trades professionals seeking Red Seal certification. Target: Apprentices, journey workers. Tone: Professional but approachable.",
    "platforms": ["linkedin_post", "facebook_post", "instagram_feed"],
    "style": "professional",
    "image_style": "photorealistic"  // Now uses proper Imagen 4 photography techniques!
  }
}
```

### Step 5: AI Generates Brand-Aware Content

**LinkedIn Post (Generated with brand context):**
```
Ready to ace your Red Seal electrician exam? 🔌⚡

Challenge Red Seal's self-paced online courses give you the flexibility
to study while you work. Learn from experienced instructors who understand
the trades.

Master the electrical theory. Practice with real exam questions.
Get certified on your schedule.

Start your journey to Red Seal certification today.

#RedSeal #ElectricianTraining #SkilledTrades #Apprenticeship #TradesCertification
```

**Image (Generated with Imagen 4 photorealism):**
- Realistic photo of electrician working
- Professional workshop environment
- 35mm lens, natural lighting, 4K quality
- NO cartoonish look - pure photography

---

## Make.com Scenario Template

```json
{
  "name": "Brand-Aware Campaign Generation",
  "modules": [
    {
      "id": 1,
      "module": "webhooks:webhook",
      "data": {
        "brand_name": "Challenge Red Seal",
        "campaign_theme": "Promote course",
        "platforms": ["linkedin_post", "facebook_post"]
      }
    },
    {
      "id": 2,
      "module": "airtable:searchRecords",
      "connection": "airtable",
      "parameters": {
        "base": "apprJV9UhYEDNL6J7",
        "table": "Brands",
        "formula": "AND({Brand Name} = '{{1.brand_name}}')"
      }
    },
    {
      "id": 3,
      "module": "util:setVariable",
      "parameters": {
        "name": "enhanced_brief",
        "value": "{{1.campaign_theme}}. Brand: {{2.Description}}. Target: {{2.Target Audience}}. Tone: {{2.Tone}}."
      }

    },
    {
      "id": 4,
      "module": "http:request",
      "parameters": {
        "url": "https://content.fastmcp.app/mcp",
        "method": "POST",
        "body": {
          "tool": "batch_generate_campaign",
          "params": {
            "campaign_brief": "{{3.enhanced_brief}}",
            "platforms": "{{1.platforms}}",
            "style": "professional",
            "image_style": "photorealistic"
          }
        }
      }
    },
    {
      "id": 5,
      "module": "iterator",
      "array": "{{4.platforms}}"
    },
    {
      "id": 6,
      "module": "airtable:createRecord",
      "parameters": {
        "base": "apprJV9UhYEDNL6J7",
        "table": "Content Pieces",
        "record": {
          "Campaign Brief": "{{1.campaign_theme}}",
          "Brand": ["{{2.id}}"],
          "Platform": "{{5.platform}}",
          "Generated Content": "{{5.content.content}}",
          "Generated Hashtags": "{{5.content.hashtag_string}}"
        }
      }
    },
    {
      "id": 7,
      "module": "airtable:createRecord",
      "parameters": {
        "base": "apprJV9UhYEDNL6J7",
        "table": "Assets",
        "record": {
          "Asset Type": "Image",
          "Base64 Data": "{{5.image.base64_data}}",
          "Platform": "{{5.platform}}",
          "Brand": ["{{2.id}}"]
        }
      }
    },
    {
      "id": 8,
      "module": "airtable:createRecord",
      "parameters": {
        "base": "apprJV9UhYEDNL6J7",
        "table": "Social Media Posts Queue",
        "record": {
          "Post Content": "{{5.content.full_post}}",
          "Platform": "{{5.platform}}",
          "Content Piece": ["{{6.id}}"],
          "Generated Asset": ["{{7.id}}"],
          "Brand": ["{{2.id}}"],
          "Status": "Pending"
        }
      }
    }
  ]
}
```

---

## What Changed with Photorealism Fix

### Before (Cartoonish):
```
Prompt: "Electrician working"
Result: Generic AI-looking illustration
```

### After (Photorealistic):
```
Prompt: "A photo of electrician working, 35mm portrait lens,
        natural lighting, 4K, HDR, Studio Photo, shot by a
        professional photographer, high detail, sharp focus,
        realistic textures. CRITICAL: Pure photographic quality,
        NOT illustration, NOT CGI, NOT cartoon style."
Result: Looks like a real professional photograph
```

**Key differences:**
- ✅ "A photo of" prefix (signals photographic intent)
- ✅ Specific lens type (35mm portrait lens)
- ✅ Photography modifiers (4K, HDR, Studio Photo)
- ✅ Explicit exclusion of cartoon/CGI/illustration

---

## Testing Right Now

### Quick Test (No Airtable, Just MCP Server):

```json
{
  "tool": "batch_generate_campaign",
  "params": {
    "campaign_brief": "Promote electrician certification course. Brand: Challenge Red Seal - online learning platform for skilled trades professionals seeking Red Seal certification. Self-paced courses. Target: Apprentices and journey workers. Tone: Professional but approachable, educational.",
    "platforms": ["linkedin_post"],
    "style": "professional",
    "image_style": "photorealistic"
  }
}
```

**Expected result:**
- LinkedIn post about electrician course
- Content mentions Red Seal, apprentices, self-paced learning
- Image looks like REAL photograph of electrician/workshop
- ~30 seconds, ~$0.04 cost

---

## Logo Overlay (Future Enhancement)

**Current limitation:** Imagen 4 can't reliably place logos.

**Solution for later:**
1. Generate clean background image (no logo)
2. Use PIL (Pillow) in separate service to overlay logo
3. Store final image with logo in Assets table

**Example with PIL:**
```python
from PIL import Image
import base64
from io import BytesIO

# Decode base64 from MCP server
img_data = base64.b64decode(base64_string.split(',')[1])
background = Image.open(BytesIO(img_data))

# Load logo
logo = Image.open("challenge-red-seal-logo.png")
logo = logo.resize((200, 200))

# Overlay logo in bottom-right corner
background.paste(logo, (background.width - 220, background.height - 220), logo)

# Save result
background.save("final_with_logo.png")
```

**Not needed right now** - start with clean professional photos first.

---

## Next Steps

1. **Test MCP server** with enhanced brief in FastMCP Cloud Inspector
2. **Verify images look real** (not cartoonish) with new photorealism
3. **Build Make.com scenario** using template above
4. **Generate first Challenge Red Seal campaign**
5. **Review results** and iterate on brand description if needed

**Focus:** Get ONE campaign working end-to-end before scaling.
