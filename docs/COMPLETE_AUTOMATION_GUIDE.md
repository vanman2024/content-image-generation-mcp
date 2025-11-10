# Complete AI-Driven Social Media Automation

## From Campaign Brief to Published Post in 30 Seconds

This guide shows how to use the new MCP tools for fully automated social media campaigns.

---

## 🚀 Quick Start: Full Campaign Automation

### Single Tool Call for Everything

```python
# One call = Complete campaign ready to post
result = batch_generate_campaign(
    campaign_brief="Announce our new AI productivity tool. Highlight time-saving benefits for busy professionals.",
    platforms=["instagram_feed", "linkedin_post", "twitter_post"],
    style="professional",
    target_audience="Marketing managers and business owners"
)

# Result includes:
# - AI-generated post content for each platform
# - AI-generated hashtags (respects platform limits)
# - Platform-optimized images (correct dimensions)
# - Base64 encoded for direct API upload
# - Ready-to-insert Airtable data

print(f"Generated {result['platforms_generated']} posts")
print(f"Cost: ${result['estimated_cost_usd']}")
print(f"Ready for posting: {result['all_ready']}")
```

---

## 📊 What Gets Generated

### For Each Platform:

1. **Content** (Gemini 2.5 Flash)
   - Platform-optimized character count
   - Appropriate tone and style
   - Platform-specific formatting

2. **Hashtags** (AI-generated)
   - Respects platform limits (LinkedIn: 5, Instagram: 30, etc.)
   - Relevant to campaign and target audience
   - Industry-appropriate

3. **Images** (Imagen 4.0)
   - Platform-optimized dimensions
   - Professional quality
   - Base64 encoded for API upload

4. **Validation**
   - Character count checks
   - Hashtag count checks
   - Platform constraint compliance

---

## 🎯 Example Output

### Input:
```json
{
  "campaign_brief": "New feature launch: AI-powered analytics dashboard",
  "platforms": ["linkedin_post", "twitter_post"],
  "style": "professional",
  "target_audience": "Marketing managers"
}
```

### Output (LinkedIn):
```json
{
  "platform": "linkedin_post",
  "content": {
    "content": "Introducing our new AI-powered analytics dashboard 📊\n\nTransform hours of manual reporting into minutes of actionable insights.\n\nBuilt for marketing teams who need to move fast without sacrificing accuracy.\n\nEarly access starts next week.",
    "hashtags": ["MarketingAnalytics", "AItools", "MarketingAutomation", "DataDriven", "ProductLaunch"],
    "hashtag_string": "#MarketingAnalytics #AItools #MarketingAutomation #DataDriven #ProductLaunch",
    "full_post": "Introducing our new AI-powered analytics dashboard 📊\n\nTransform hours of manual reporting into minutes of actionable insights.\n\nBuilt for marketing teams who need to move fast without sacrificing accuracy.\n\nEarly access starts next week. #MarketingAnalytics #AItools #MarketingAutomation #DataDriven #ProductLaunch",
    "character_count": 287,
    "character_limit": 3000,
    "within_character_limit": true,
    "hashtag_count": 5,
    "hashtag_limit": 5,
    "within_hashtag_limit": true,
    "all_valid": true
  },
  "image": {
    "success": true,
    "filename": "linkedin_post_20251110_123456.png",
    "local_path": "/tmp/linkedin_post_20251110_123456.png",
    "dimensions": "1200x627",
    "base64_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "base64_size_kb": 245.67
  },
  "ready_for_posting": true,
  "airtable_data": {
    "Post Content": "Introducing our new AI-powered analytics dashboard 📊...",
    "Platform": "linkedin_post",
    "Generated Hashtags": "#MarketingAnalytics #AItools...",
    "Base64 Image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "Character Count": 287,
    "Hashtag Count": 5,
    "Content Valid": true,
    "Campaign Brief": "New feature launch: AI-powered analytics dashboard"
  }
}
```

---

## 🔧 Available Tools

### 1. `generate_campaign_content` - Content Only

Generate AI-written posts without images (faster, cheaper for testing).

```python
result = generate_campaign_content(
    campaign_brief="Promote summer sale with beach theme",
    platforms=["instagram_feed", "facebook_post", "twitter_post"],
    style="casual",  # Options: professional, casual, humorous, educational, promotional
    hashtag_strategy="trending",  # Options: industry-specific, trending, branded, niche
    target_audience="Young adults 18-30",
    include_cta=True  # Include call-to-action
)

# Result
{
  "success": true,
  "generated_count": 3,
  "ready_for_posting": true,
  "platforms": [
    {
      "platform": "instagram_feed",
      "content": "Summer vibes incoming! ☀️🌊...",
      "hashtags": ["SummerSale", "BeachLife", "SummerVibes"],
      "character_count": 145,
      "all_valid": true
    },
    # ... more platforms
  ]
}
```

**Cost:** ~$0.0015 per campaign (Gemini is cheap!)

---

### 2. `batch_generate_campaign` - Complete Automation

Generate content + images for all platforms.

```python
result = batch_generate_campaign(
    campaign_brief="Launch new eco-friendly product line",
    platforms=["instagram_feed", "facebook_post", "linkedin_post", "pinterest_pin"],
    style="professional",
    target_audience="Environmentally conscious consumers",
    image_style="photorealistic",  # Options: photorealistic, illustrated, 3d, modern
    include_base64=True  # Always true for social media posting
)

# Result
{
  "success": true,
  "platforms_generated": 4,
  "ready_for_posting": 4,
  "all_ready": true,
  "estimated_cost_usd": 0.1615,  # 4 images × $0.04 + Gemini
  "platforms": [
    {
      "platform": "instagram_feed",
      "content": {...},  # AI-generated content
      "image": {...},    # Generated image with base64
      "ready_for_posting": true,
      "airtable_data": {...}  # Ready to insert
    },
    # ... more platforms
  ]
}
```

**Cost:** ~$0.04 per image + $0.0015 for content = ~$0.16 for 4-platform campaign

---

## 🤖 Make.com Integration Workflow

### Complete Automation: Brief → Posting

```
┌─────────────────────────────────────┐
│ Step 1: Trigger (Webhook/Form)     │
│ Input: Campaign brief + platforms  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 2: HTTP Request to MCP Server │
│ Tool: batch_generate_campaign       │
│                                     │
│ POST https://content.fastmcp.app/   │
│ {                                   │
│   "tool": "batch_generate_campaign",│
│   "params": {                       │
│     "campaign_brief": "...",        │
│     "platforms": ["instagram"...]   │
│   }                                 │
│ }                                   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 3: Iterator (for each platform│
│ Loop through result.platforms[]     │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 4: Create Content Piece        │
│ Airtable > Create Record            │
│                                     │
│ Table: Content Pieces               │
│ Fields:                             │
│   - Campaign Brief                  │
│   - Platform (link)                 │
│   - Generated Content               │
│   - Generated Hashtags              │
│   - Content Status: "Ready"         │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 5: Create Asset                │
│ Airtable > Create Record            │
│                                     │
│ Table: Assets                       │
│ Fields:                             │
│   - Asset Type: "Image"             │
│   - Base64 Data                     │
│   - Platform (link)                 │
│   - Generation Cost                 │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 6: Create Social Post Queue   │
│ Airtable > Create Record            │
│                                     │
│ Table: Social Media Posts Queue     │
│ Fields:                             │
│   - Post Content (from Step 4)      │
│   - Platform (link)                 │
│   - Content Piece (link to Step 4)  │
│   - Generated Asset (link to Step 5)│
│   - Status: "Pending" ← TRIGGER!    │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 7: Airtable Automation         │
│ Triggered by Status = "Pending"     │
│                                     │
│ → Calls Ayrshare API                │
│ → Posts to social media             │
│ → Updates Status = "Posted"         │
│ → Stores Posted URL                 │
└─────────────────────────────────────┘
```

---

## 💰 Cost Analysis

### Per Campaign (4 platforms)

| Item | Quantity | Unit Cost | Total |
|------|----------|-----------|-------|
| Gemini 2.5 Flash (content) | 4 generations (~6K tokens) | $0.00037 | $0.0015 |
| Imagen 4.0 (images) | 4 images (1024x1024) | $0.04 | $0.16 |
| Ayrshare API | 4 posts | $0 (free tier) | $0 |
| Make.com operations | ~20 operations | $0.009 | $0.18 |
| **TOTAL** | | | **$0.34** |

### Monthly at Scale

- 100 campaigns/month = $34
- 500 campaigns/month = $170
- 1000 campaigns/month = $340

**Compare to hiring a social media manager:** $3,000-5,000/month

**ROI:** 10-15x cost savings

---

## 📝 Make.com Scenario Template

### JSON Blueprint (Import Directly)

```json
{
  "name": "AI Social Media Campaign Automation",
  "flow": [
    {
      "id": 1,
      "module": "webhooks:webhook",
      "parameters": {
        "hook": {
          "name": "Campaign Trigger",
          "dataStructure": {
            "campaign_brief": "string",
            "platforms": ["string"],
            "style": "string",
            "target_audience": "string"
          }
        }
      }
    },
    {
      "id": 2,
      "module": "http:request",
      "parameters": {
        "url": "https://content.fastmcp.app/mcp",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "tool": "batch_generate_campaign",
          "params": {
            "campaign_brief": "{{1.campaign_brief}}",
            "platforms": "{{1.platforms}}",
            "style": "{{1.style}}",
            "target_audience": "{{1.target_audience}}"
          }
        }
      }
    },
    {
      "id": 3,
      "module": "builtin:iterator",
      "iterator": "{{2.platforms}}"
    },
    {
      "id": 4,
      "module": "airtable:createRecord",
      "parameters": {
        "base": "YOUR_BASE_ID",
        "table": "Content Pieces",
        "typecast": true,
        "record": {
          "Campaign Brief": "{{1.campaign_brief}}",
          "Platform": "{{3.platform}}",
          "Generated Content": "{{3.content.content}}",
          "Generated Hashtags": "{{3.content.hashtag_string}}",
          "Content Status": "Ready"
        }
      }
    },
    {
      "id": 5,
      "module": "airtable:createRecord",
      "parameters": {
        "base": "YOUR_BASE_ID",
        "table": "Assets",
        "typecast": true,
        "record": {
          "Asset Type": "Image",
          "Base64 Data": "{{3.image.base64_data}}",
          "Platform": "{{3.platform}}",
          "Generation Cost": "{{3.image.estimated_cost_usd}}"
        }
      }
    },
    {
      "id": 6,
      "module": "airtable:createRecord",
      "parameters": {
        "base": "YOUR_BASE_ID",
        "table": "Social Media Posts Queue",
        "typecast": true,
        "record": {
          "Post Content": "{{3.content.full_post}}",
          "Platform": "{{3.platform}}",
          "Content Piece": ["{{4.id}}"],
          "Generated Asset": ["{{5.id}}"],
          "Status": "Pending"
        }
      }
    }
  ]
}
```

**Operations per campaign:** ~20 (well within Make.com free tier of 1,000/month)

---

## 🎨 Style Options

### Content Styles
- `professional` - Corporate, polished, business-focused
- `casual` - Friendly, conversational, approachable
- `humorous` - Funny, entertaining, memorable
- `educational` - Informative, value-driven, teaching
- `promotional` - Sales-focused, offer-driven, urgent

### Hashtag Strategies
- `industry-specific` - Niche hashtags for industry professionals
- `trending` - Popular, high-volume hashtags
- `branded` - Company/product-specific hashtags
- `niche` - Micro-community hashtags

### Image Styles
- `photorealistic` - Professional photography quality
- `illustrated` - Hand-drawn, artistic style
- `3d` - 3D rendered, modern aesthetic
- `modern` - Clean, minimalist, contemporary

---

## 🧪 Testing the Tools

### Test 1: Content Only (Fast & Cheap)

```bash
# In FastMCP Cloud Inspector
{
  "tool": "generate_campaign_content",
  "params": {
    "campaign_brief": "Test campaign: New product launch",
    "platforms": ["linkedin_post"],
    "style": "professional"
  }
}

# Expected result: Content generated in ~2 seconds, cost: $0.0004
```

### Test 2: Full Campaign (3 platforms)

```bash
{
  "tool": "batch_generate_campaign",
  "params": {
    "campaign_brief": "Promote our new AI writing assistant tool",
    "platforms": ["instagram_feed", "linkedin_post", "twitter_post"],
    "style": "professional",
    "target_audience": "Content creators and marketers"
  }
}

# Expected result: Complete campaign in ~30 seconds, cost: ~$0.12
```

---

## 📊 Monitoring & Analytics

### Track Campaign Performance

Add these fields to "Social Media Posts Queue" table:

1. **Engagement Rate** (Number)
   - Manual entry from platform analytics

2. **Reach** (Number)
   - Total impressions from platform

3. **Clicks** (Number)
   - Link clicks (if CTA included)

4. **Cost Per Post** (Currency)
   - From generation cost

5. **ROI** (Formula)
   ```javascript
   ({Engagement Rate} * 100) / {Cost Per Post}
   ```

---

## 🚨 Error Handling

### Common Issues

**1. Character Limit Exceeded**
```json
{
  "platform": "twitter_post",
  "all_valid": false,
  "within_character_limit": false,
  "character_count": 295,
  "character_limit": 280
}
```
**Fix:** Re-generate with more restrictive prompt or edit content manually

**2. Image Generation Failed**
```json
{
  "platform": "instagram_feed",
  "image": {
    "success": false,
    "error": "Safety filter triggered"
  }
}
```
**Fix:** Modify campaign brief to remove potentially sensitive terms

**3. Invalid Platform**
```json
{
  "platform": "snapchat_story",
  "success": false,
  "error": "Platform 'snapchat_story' not found in PLATFORM_SPECS"
}
```
**Fix:** Use valid platform keys (see PLATFORM_SPECS in server.py)

---

## 🎯 Next Steps

1. **Test in FastMCP Cloud Inspector**
   - Try generate_campaign_content first
   - Then try batch_generate_campaign

2. **Set Up Make.com Scenario**
   - Import JSON blueprint
   - Connect to your Airtable base
   - Test with webhook trigger

3. **Configure Airtable Automation**
   - Already done! (AIRTABLE_AUTOMATION_SCRIPT.js)
   - Add your Ayrshare API key
   - Test with Status = "Pending"

4. **Scale Up**
   - Create batch campaigns
   - Schedule posts for optimal times
   - Track performance metrics

---

## 💡 Pro Tips

1. **Start Small:** Test with 1 platform before scaling to 6+

2. **Review Before Posting:** Set Status = "Draft" initially, review AI content, then change to "Pending"

3. **A/B Test Styles:** Try "professional" vs "casual" and track engagement

4. **Reuse Assets:** Link same Generated Asset to multiple Content Pieces

5. **Schedule Wisely:** Use platform "Best Posting Times" from Airtable specs

6. **Monitor Costs:** Track total generation costs in Assets table

7. **Iterate Prompts:** Refine campaign briefs based on what performs well

---

**Full automation is now ready! 🚀**

Input: Campaign brief
Output: Published social media posts
Time: 30 seconds
Cost: ~$0.08-0.20 per platform
Human effort: Zero (after initial Make.com setup)
