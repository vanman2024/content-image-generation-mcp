# AI-Driven Social Media Pipeline

## Complete Automation: Campaign → Content → Images → Posting

**Problem:** Manual entry of posts is not scalable
**Solution:** Fully AI-driven pipeline from campaign brief to published posts

---

## Architecture Overview

```
Campaign Brief (1 input)
    ↓
AI Content Generator (Gemini 2.5 Flash)
    ├─ Generates post content for each platform
    ├─ Platform-specific character optimization
    ├─ AI-generated hashtags (respects platform limits)
    └─ Creates records in "Content Pieces" table
    ↓
AI Image Generator (Imagen 4.0)
    ├─ Generates images for each platform
    ├─ Platform-optimized dimensions
    └─ Creates records in "Assets" table
    ↓
Social Posts Queue (auto-populated)
    ├─ Links to Content Piece
    ├─ Links to Platform
    ├─ Links to Generated Asset
    └─ Status = "Pending"
    ↓
Airtable Automation (triggered)
    ├─ Posts to Ayrshare API
    └─ Updates Status = "Posted"
```

**Input:** 1 campaign brief
**Output:** 6-12 platform-specific posts published automatically

---

## Table Structure: Content Pieces (NEW)

**Purpose:** Store AI-generated content before it goes to posting queue

### Core Fields

1. **Campaign Brief** (Long Text)
   - Single input: "Promote summer sale with beach theme, casual tone, limited time offer"

2. **Platform** (Link to Platforms)
   - Single platform this content is for

3. **Generated Content** (Long Text)
   - AI-generated post text from Gemini 2.5 Flash
   - Auto-optimized for platform character limits

4. **Generated Hashtags** (Long Text)
   - AI-generated hashtags (comma-separated)
   - Respects platform hashtag limits

5. **Content Status** (Single Select)
   - Options: `Generating`, `Ready`, `Queued`, `Posted`, `Failed`

6. **Theme/Style** (Single Select)
   - Options: `Professional`, `Casual`, `Humorous`, `Educational`, `Promotional`

7. **Target Audience** (Single Line Text)
   - "Young professionals", "Parents", "Tech enthusiasts", etc.

### Auto-Generated Fields

8. **Character Count** (Formula)
   ```javascript
   LEN({Generated Content})
   ```

9. **Hashtag Count** (Formula)
   ```javascript
   LEN({Generated Hashtags}) - LEN(SUBSTITUTE({Generated Hashtags}, ",", "")) + 1
   ```

10. **Content Valid** (Formula - Checkbox)
    ```javascript
    AND(
      {Character Count} <= {Max Character Count (From Platform)},
      {Hashtag Count} <= {Hashtag Limit (From Platform)}
    )
    ```

---

## Workflow 1: Bulk Campaign Content Generation

### Input
```json
{
  "campaign_brief": "Announce our new AI assistant product. Professional tone, highlight time-saving benefits, target small business owners.",
  "platforms": ["instagram", "linkedin", "twitter", "facebook"],
  "style": "professional",
  "hashtag_strategy": "industry-specific"
}
```

### MCP Tool: `generate_campaign_content`

```python
@mcp.tool()
def generate_campaign_content(
    campaign_brief: str,
    platforms: List[str],
    style: str = "professional",
    hashtag_strategy: str = "industry-specific",
    target_audience: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate platform-optimized content for a campaign across multiple platforms.

    Uses Gemini 2.5 Flash to create:
    - Platform-specific post content (respecting character limits)
    - Relevant hashtags (respecting hashtag limits)
    - Call-to-action variations

    Returns structured data ready for Airtable insertion.
    """

    results = []

    for platform in platforms:
        # Get platform specs
        platform_spec = PLATFORM_SPECS.get(platform)
        if not platform_spec:
            continue

        # Create platform-specific prompt
        prompt = f"""
You are a professional social media content creator.

CAMPAIGN BRIEF: {campaign_brief}
PLATFORM: {platform}
STYLE: {style}
TARGET AUDIENCE: {target_audience or "general audience"}

PLATFORM CONSTRAINTS:
- Max characters: {platform_spec['max_chars']}
- Max hashtags: {platform_spec['max_hashtags']}
- Caption style: {platform_spec['caption_style']}

TASK:
1. Create engaging post content that fits within character limit
2. Generate {platform_spec['max_hashtags']} relevant hashtags for {hashtag_strategy} strategy
3. Include platform-appropriate call-to-action
4. Match the {style} tone

OUTPUT FORMAT (JSON):
{{
  "content": "The post text with emojis if appropriate",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
  "cta": "Call to action text"
}}

IMPORTANT:
- Instagram/Facebook: Emojis encouraged, hashtags at end
- LinkedIn: Professional tone, fewer hashtags (5 max)
- Twitter: Concise, strong hook, hashtags integrated
- DO NOT exceed character or hashtag limits
"""

        # Generate content using Gemini 2.5 Flash
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview",
            contents=prompt,
            config=GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=1000,
                response_mime_type="application/json"
            )
        )

        content_data = json.loads(response.text)

        # Validate character count
        full_content = f"{content_data['content']} {' '.join(['#' + h for h in content_data['hashtags']])}"
        char_count = len(full_content)

        results.append({
            "platform": platform,
            "content": content_data['content'],
            "hashtags": content_data['hashtags'],
            "hashtag_string": ", ".join(content_data['hashtags']),
            "cta": content_data['cta'],
            "character_count": char_count,
            "character_limit": platform_spec['max_chars'],
            "within_limit": char_count <= platform_spec['max_chars'],
            "hashtag_count": len(content_data['hashtags']),
            "hashtag_limit": platform_spec['max_hashtags']
        })

    return {
        "campaign_brief": campaign_brief,
        "generated_count": len(results),
        "platforms": results,
        "ready_for_airtable": True
    }
```

---

## Workflow 2: Airtable Integration with Make.com

### Trigger 1: New Campaign Brief Entered

**Make.com Scenario:**

```
Module 1: Webhook/Manual Trigger
  Input: Campaign brief, platforms, style
  ↓
Module 2: HTTP Request to MCP Server
  URL: https://content.fastmcp.app/mcp
  Method: POST
  Body: {
    "tool": "generate_campaign_content",
    "params": {
      "campaign_brief": "{{campaign_brief}}",
      "platforms": {{platforms}},
      "style": "{{style}}"
    }
  }
  ↓
Module 3: Iterator (for each platform result)
  ↓
Module 4: Airtable > Create Record (Content Pieces)
  Fields:
    - Campaign Brief: {{campaign_brief}}
    - Platform: Link to Platform record
    - Generated Content: {{content}}
    - Generated Hashtags: {{hashtag_string}}
    - Content Status: "Ready"
  ↓
Module 5: HTTP Request to MCP Server (Generate Image)
  URL: https://content.fastmcp.app/mcp
  Body: {
    "tool": "generate_social_media_image",
    "params": {
      "description": "{{campaign_brief}}",
      "platform": "{{platform}}",
      "include_base64": true
    }
  }
  ↓
Module 6: Airtable > Create Record (Assets)
  Fields:
    - Asset Type: "Image"
    - Base64 Data: {{base64_data}}
    - Platform: Link to Platform
    - Generation Cost: {{cost_usd}}
  ↓
Module 7: Airtable > Create Record (Social Media Posts Queue)
  Fields:
    - Post Content: {{content}} + " " + {{hashtags}}
    - Platform: Link to Platform
    - Content Piece: Link to created Content Piece
    - Generated Asset: Link to created Asset
    - Status: "Pending"  ← This triggers your existing automation!
```

**Result:** Fully automated from brief to posting

---

## Workflow 3: Content Review Before Posting (Optional)

If you want human review:

```
Same as Workflow 2, but:
  ↓
Module 7: Create with Status = "Draft" (not "Pending")
  ↓
[HUMAN REVIEW IN AIRTABLE]
  - Review generated content
  - Edit if needed
  - Change Status to "Pending"
  ↓
Existing Airtable Automation posts via Ayrshare
```

---

## Enhanced Social Media Posts Queue Table

Update your existing table with these fields:

### New Fields to Add

1. **Content Piece** (Link to Content Pieces)
   - Links back to AI-generated content
   - Shows campaign context

2. **Hashtags** (Long Text)
   - Lookup from Content Piece → Generated Hashtags
   - Can be overridden manually

3. **Full Post** (Formula)
   ```javascript
   // Combines content + hashtags for platform
   IF(
     {Generated Hashtags},
     {Post Content} & " " & {Generated Hashtags},
     {Post Content}
   )
   ```

4. **AI Generated** (Checkbox)
   - Auto-checked if Content Piece exists
   - Helps track manual vs AI posts

---

## Cost Estimation

### Per Campaign (6 platforms)

| Service | Usage | Cost |
|---------|-------|------|
| Gemini 2.5 Flash | 6 content generations (~6K tokens) | $0.0015 |
| Imagen 4.0 | 6 images (1024x1024) | $0.24 |
| Ayrshare API | 6 posts | $0 (free tier) |
| **Total** | | **~$0.25 per campaign** |

### Monthly at Scale

- 100 campaigns/month = $25
- 500 campaigns/month = $125
- 1000 campaigns/month = $250

**Make.com:** $9/month for 1,000 operations (enough for ~150 campaigns)

---

## Implementation Steps

### Phase 1: Add MCP Tools
1. ✅ Add `generate_campaign_content` tool to server.py
2. ✅ Add `batch_generate_campaign` for full automation
3. ✅ Add `validate_content_for_platform` for QA

### Phase 2: Update Airtable
1. Create "Content Pieces" table
2. Add fields to "Social Media Posts Queue"
3. Link tables properly

### Phase 3: Make.com Setup
1. Create scenario for campaign → content → images → queue
2. Add error handling and notifications
3. Test with single platform first

### Phase 4: Scale
1. Add batch campaign processing
2. Add scheduling intelligence (best posting times)
3. Add A/B testing variants

---

## Example: Complete Campaign Flow

### Input (in Make.com form)
```json
{
  "campaign_brief": "New feature launch: AI-powered analytics dashboard. Highlight ease of use and time savings.",
  "platforms": ["linkedin", "twitter", "facebook"],
  "style": "professional",
  "target_audience": "Marketing managers and analysts"
}
```

### AI Generated Content (Gemini 2.5 Flash)

**LinkedIn:**
```
Content: "Introducing our new AI-powered analytics dashboard 📊
Transform hours of manual reporting into minutes of actionable insights.
Built for marketing teams who need to move fast without sacrificing accuracy.
Early access starts next week."

Hashtags: #MarketingAnalytics, #AItools, #MarketingAutomation, #DataDriven, #ProductLaunch

Character Count: 287 / 3000 ✅
Hashtag Count: 5 / 5 ✅
```

**Twitter:**
```
Content: "Tired of manual analytics reporting? 😴
Our new AI dashboard does it in minutes, not hours.
Early access launching next week → 🔗

Hashtags: #MarTech, #AIanalytics, #ProductLaunch

Character Count: 178 / 280 ✅
Hashtag Count: 3 / 10 ✅
```

**Facebook:**
```
Content: "📊 Big news for marketing teams!

We just launched an AI-powered analytics dashboard that cuts reporting time by 80%.

No more manual data crunching. No more spreadsheet headaches. Just insights that help you make better decisions faster.

Early access starts next week – comment 'ACCESS' to get on the list! 👇"

Hashtags: #MarketingTools, #AIinMarketing, #AnalyticsDashboard, #MarketingAutomation

Character Count: 398 / 63206 ✅
Hashtag Count: 4 / 10 ✅
```

### AI Generated Images (Imagen 4.0)

**LinkedIn (1200x627):**
- Professional dashboard screenshot mockup
- Clean corporate aesthetic
- Data visualization focus

**Twitter (1200x675):**
- Eye-catching before/after comparison
- Bright colors for feed visibility
- Clear product benefit

**Facebook (1200x630):**
- Engaging lifestyle image
- Relatable marketing team scenario
- Product UI overlay

### Result in Airtable

**Content Pieces Table:** 3 records created
**Assets Table:** 3 images generated
**Social Posts Queue:** 3 records with Status = "Pending"
**Automation:** Posts to all 3 platforms within 1 minute

**Total Time:** ~30 seconds
**Total Cost:** ~$0.13
**Human Effort:** 0 (fully automated)

---

## Next Steps

1. **Add MCP tools** - Implement generate_campaign_content
2. **Test single platform** - Generate content for just Instagram
3. **Create Make.com scenario** - Build automation pipeline
4. **Scale to all platforms** - Expand to full campaign generation

Should I start implementing the MCP tools for AI content generation?
