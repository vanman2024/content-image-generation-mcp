# Usage Examples: Content & Image Generation MCP Server

## Quick Start Examples

### 1. Single Platform Social Image

```python
# Generate Instagram post
result = generate_social_media_image(
    platform="instagram_feed",
    description="bear relaxing in pool with sunglasses and Coke",
    primary_text="Summer Vibes 🌊",
    style="photorealistic"
)

# Result includes:
# - local_path: "/path/to/instagram_feed_20250109_143022.png"
# - base64_data: "data:image/png;base64,iVBORw0KG..." (ready for API upload!)
# - file_size_mb: 1.2
# - estimated_cost_usd: 0.04

# Upload to Instagram Graph API
instagram_api.create_post(
    image_data=result["base64_data"],
    caption="Living the dream! #SummerVibes #BearLife"
)
```

### 2. Multi-Platform Campaign

```python
# Generate complete social campaign
campaign = batch_generate_social_set(
    description="new product launch - sleek smartphone on minimalist desk",
    platforms=[
        "instagram_feed",      # Square 1:1
        "instagram_story",     # Vertical 9:16
        "twitter_post",        # Landscape 16:9
        "linkedin_post",       # Landscape 16:9
        "pinterest_pin"        # Vertical 3:4
    ],
    primary_text="Introducing Galaxy X",
    style="modern_minimal"
)

# Results:
# {
#   "success": true,
#   "total_platforms": 5,
#   "successful": 5,
#   "total_cost_usd": 0.20,  # 5 × $0.04
#   "results": {
#     "instagram_feed": { base64_data, local_path, ... },
#     "twitter_post": { base64_data, local_path, ... },
#     ...
#   }
# }

# Upload to all platforms
for platform, data in campaign["results"].items():
    if data["success"]:
        platform_api[platform].create_post(
            image_data=data["base64_data"],
            caption=f"Introducing Galaxy X - {platform_specific_copy[platform]}"
        )
```

### 3. Photorealistic Images (Cinema Quality)

```python
# First, enhance the prompt for maximum realism
enhanced = enhance_prompt_for_photorealism(
    basic_prompt="bear in swimming pool with sunglasses and Coke"
)

# Use the enhanced prompt
result = generate_image_imagen3(
    prompt=enhanced["enhanced_prompt"],
    negative_prompt=", ".join(enhanced["negative_prompt_suggestions"]),
    aspect_ratio="16:9",
    image_size="2K",
    model_version="imagen-4.0"
)

# Enhanced prompt includes:
# - Camera specs (RED Komodo 6K, 85mm f/1.4)
# - Lighting details (golden hour, soft shadows)
# - Material textures (fur details, reflections, imperfections)
# - "No CGI, no cartoon elements" to prevent AI artifacts
```

### 4. Video with Native Audio

```python
# Generate video with dialogue and sound effects
result = generate_video_veo3(
    prompt="""
    A photorealistic 8-second video: A bear wearing sunglasses relaxes in a
    backyard swimming pool, holding a glass of Coca-Cola with ice.

    AUDIO: Water splashing gently, ice cubes clinking in the glass, summer
    birds chirping in the background. Suddenly, a person appears at the pool
    edge and exclaims "Oh my God, there's a bear in the pool!" in a shocked,
    surprised voice. The bear casually takes a sip, completely unbothered.

    Bright sunny day, natural lighting, professional cinematography.
    """,
    duration_seconds=8,
    resolution="720p",
    aspect_ratio="16:9"
)

# Video automatically includes:
# - Dialogue (person's exclamation)
# - Sound effects (water, ice, birds)
# - Ambient sound (summer atmosphere)
# - No separate audio endpoint needed!
# - Cost: $6.00 (8s × $0.75/s)
```

### 5. Batch Image Generation

```python
# Generate multiple variations
campaign_images = batch_generate_images(
    prompts=[
        "Professional product photo: smartphone on wooden desk, morning light",
        "Lifestyle shot: person using smartphone in modern coffee shop",
        "Close-up: smartphone camera lenses, dramatic lighting",
        "Flat lay: smartphone with accessories on marble surface"
    ],
    aspect_ratio="1:1",
    image_size="2K",
    model_version="imagen-4.0"
)

# Results:
# {
#   "success": true,
#   "total_images": 4,
#   "successful": 4,
#   "failed": 0,
#   "total_cost_usd": 0.32,  # 4 × $0.08 (2K)
#   "results": [ ... ]
# }
```

### 6. Content Generation with Context

```python
# Generate social media caption
content = generate_marketing_content(
    content_type="social_media_caption",
    product_name="Galaxy X Smartphone",
    key_points=[
        "Ultra-thin 6.8mm design",
        "120Hz OLED display",
        "48-hour battery life",
        "AI-powered camera"
    ],
    tone="exciting",
    platform="instagram",
    max_length=150
)

# Returns optimized caption with hashtags
```

### 7. Cost Estimation

```python
# Estimate campaign costs before generating
estimate = calculate_cost_estimate(
    images_1k=5,          # Instagram posts
    images_2k=2,          # Website hero images
    video_seconds=24,     # 3 × 8-second videos
    content_pieces=10,    # Social captions
    image_model="imagen-4.0",
    video_model="veo3"
)

# Results:
# {
#   "breakdown": {
#     "images": {
#       "1k_resolution": { count: 5, cost_usd: 0.20 },
#       "2k_resolution": { count: 2, cost_usd: 0.16 }
#     },
#     "video": { seconds: 24, cost_usd: 18.00 },
#     "content": { pieces: 10, cost_usd: 0.003 }
#   },
#   "total_cost_usd": 18.36
# }
```

---

## Platform-Specific Examples

### Instagram Campaign

```python
# Feed post (1:1 square)
feed = generate_social_media_image(
    platform="instagram_feed",
    description="product showcase - modern headphones on pastel background",
    style="modern_minimal"
)

# Story (9:16 vertical)
story = generate_social_media_image(
    platform="instagram_story",
    description="lifestyle shot - person wearing headphones, urban setting",
    primary_text="New Drop",
    style="bold_vibrant"
)

# Reels cover (9:16 vertical)
reel = generate_social_media_image(
    platform="instagram_reel",
    description="dynamic action shot - headphones with sound waves",
    style="bold_vibrant"
)
```

### LinkedIn Professional Content

```python
linkedin = generate_social_media_image(
    platform="linkedin_post",
    description="professional office environment - team collaboration meeting",
    primary_text="Innovation at Work",
    style="elegant"
)

# Upload to LinkedIn API
linkedin_api.create_share(
    image_data=linkedin["base64_data"],
    commentary="Proud to announce our Q1 results...",
    visibility="PUBLIC"
)
```

### Pinterest Pins

```python
pin = generate_social_media_image(
    platform="pinterest_pin",
    description="recipe presentation - gourmet pasta dish with fresh ingredients",
    primary_text="5-Minute Pasta",
    style="photorealistic"
)

# Pinterest API upload
pinterest_api.create_pin(
    image_base64=pin["base64_data"],
    title="Quick Gourmet Pasta Recipe",
    description="Delicious pasta in just 5 minutes...",
    link="https://yourblog.com/pasta-recipe"
)
```

### YouTube Thumbnails

```python
thumbnail = generate_social_media_image(
    platform="youtube_thumbnail",
    description="dramatic tech review setup - smartphone with dramatic lighting",
    primary_text="iPhone 16 Review",
    style="bold_vibrant"
)

# YouTube API upload
youtube_api.set_thumbnail(
    video_id="dQw4w9WgXcQ",
    thumbnail_data=thumbnail["base64_data"]
)
```

---

## Advanced Workflows

### Full Marketing Campaign Automation

```python
def launch_product_campaign(product_name, product_description):
    """
    Complete automated marketing campaign:
    1. Generate all social images
    2. Generate marketing copy
    3. Upload to all platforms
    """

    # Generate multi-platform images
    images = batch_generate_social_set(
        description=f"professional {product_name} showcase - {product_description}",
        platforms=[
            "instagram_feed",
            "twitter_post",
            "linkedin_post",
            "facebook_post",
            "pinterest_pin"
        ],
        primary_text=f"Introducing {product_name}",
        style="modern_minimal"
    )

    # Generate marketing copy for each platform
    captions = {
        "instagram": generate_marketing_content(
            content_type="social_media_caption",
            product_name=product_name,
            tone="exciting",
            platform="instagram"
        ),
        "twitter": generate_marketing_content(
            content_type="social_media_caption",
            product_name=product_name,
            tone="informative",
            platform="twitter",
            max_length=280
        ),
        "linkedin": generate_marketing_content(
            content_type="social_media_caption",
            product_name=product_name,
            tone="professional",
            platform="linkedin"
        )
    }

    # Upload to all platforms
    results = {}
    for platform, image_data in images["results"].items():
        if image_data["success"]:
            # Get platform-specific API
            api = get_platform_api(platform)

            # Upload with caption
            caption = captions.get(platform.split("_")[0], "")

            result = api.create_post(
                image_data=image_data["base64_data"],
                caption=caption
            )

            results[platform] = result

    return {
        "images_generated": images["successful"],
        "total_cost": images["total_cost_usd"],
        "platforms_posted": len(results),
        "post_urls": results
    }

# Launch campaign
campaign = launch_product_campaign(
    product_name="Galaxy X Pro",
    product_description="ultra-thin flagship smartphone with AI camera"
)
```

---

## Best Practices

### 1. Use Photorealism Enhancement
```python
# GOOD: Enhanced prompt
enhanced = enhance_prompt_for_photorealism("bear in pool")
generate_image_imagen3(prompt=enhanced["enhanced_prompt"])

# NOT AS GOOD: Basic prompt
generate_image_imagen3(prompt="bear in pool")
```

### 2. Platform-Specific Generation
```python
# GOOD: Use platform presets
generate_social_media_image(platform="instagram_feed", ...)

# LESS OPTIMAL: Generic generation with wrong aspect ratio
generate_image_imagen3(aspect_ratio="16:9", ...)  # Wrong for Instagram!
```

### 3. Batch Operations for Efficiency
```python
# GOOD: Batch generation
batch_generate_social_set(platforms=[...])

# LESS EFFICIENT: Individual calls
for platform in platforms:
    generate_social_media_image(platform=platform, ...)
```

### 4. Cost Awareness
```python
# ALWAYS estimate first for expensive operations
estimate = calculate_cost_estimate(video_seconds=24)
if estimate["total_cost_usd"] < budget:
    # Proceed with generation
    generate_video_veo3(...)
```

---

## Integration Examples

### WordPress Integration
```python
result = generate_social_media_image(
    platform="blog_featured",
    description="article topic visualization"
)

# Upload to WordPress
wordpress.media.upload(
    file=result["local_path"],
    post_id=post_id
)
```

### Shopify Product Images
```python
product_image = generate_social_media_image(
    platform="instagram_feed",
    description=f"ecommerce product photo - {product.name}",
    style="modern_minimal"
)

# Upload to Shopify
shopify.products.add_image(
    product_id=product.id,
    image_data=product_image["base64_data"]
)
```

### Email Marketing (Mailchimp)
```python
header = generate_social_media_image(
    platform="email_header",
    description="seasonal campaign header - summer sale",
    style="bold_vibrant"
)

# For email, you'd typically upload to your CDN first
# Then use the public URL in the email template
```

---

## Tips & Tricks

1. **Include audio cues in video prompts** using quotes for dialogue
2. **Use negative prompts** to avoid cartoon/CGI look in images
3. **Batch generate** multiple platforms to save time
4. **Estimate costs** before generating expensive videos
5. **Use base64 data** for direct platform API uploads (no URL needed!)
6. **Platform presets** automatically optimize dimensions
7. **Style consistency** across campaigns using style parameter
8. **Primary text** helps compositional AI for text overlay space
