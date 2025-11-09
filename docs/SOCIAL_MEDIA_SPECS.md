# Social Media & Web Platform Image Specifications

## The Problem

Different platforms require different image sizes, aspect ratios, and formats for optimal display.

## Platform Specifications

### Instagram
- **Feed Post:** 1080x1080px (1:1 square)
- **Story:** 1080x1920px (9:16 vertical)
- **Reels Cover:** 1080x1920px (9:16 vertical)
- **Carousel:** 1080x1080px (1:1 square)
- **Profile Picture:** 320x320px (1:1 square)

### Facebook
- **Feed Post:** 1200x630px (1.91:1)
- **Story:** 1080x1920px (9:16 vertical)
- **Cover Photo:** 820x312px (2.7:1)
- **Event Cover:** 1920x1005px (1.91:1)
- **Profile Picture:** 180x180px (1:1 square)

### Twitter/X
- **Feed Post:** 1200x675px (16:9)
- **Header:** 1500x500px (3:1)
- **Profile Picture:** 400x400px (1:1 square)
- **Card Image:** 1200x628px (1.91:1)

### LinkedIn
- **Feed Post:** 1200x627px (1.91:1)
- **Article Cover:** 1200x627px (1.91:1)
- **Company Logo:** 300x300px (1:1 square)
- **Background Photo:** 1584x396px (4:1)

### Pinterest
- **Standard Pin:** 1000x1500px (2:3 vertical)
- **Long Pin:** 1000x2100px (optimized)
- **Square Pin:** 1000x1000px (1:1)

### YouTube
- **Thumbnail:** 1280x720px (16:9)
- **Channel Banner:** 2560x1440px (16:9)
- **Channel Icon:** 800x800px (1:1 square)

### TikTok
- **Video Cover:** 1080x1920px (9:16 vertical)
- **Profile Picture:** 200x200px (1:1 square)

### Website/Blog
- **Hero Image:** 1920x1080px (16:9)
- **Blog Featured:** 1200x630px (1.91:1)
- **Blog Inline:** 800x600px (4:3)
- **Thumbnail:** 400x300px (4:3)

### Email Marketing
- **Header Image:** 600x200px (3:1)
- **Featured Image:** 600x400px (3:2)
- **Inline Image:** 600x600px (1:1)

---

## Imagen Size Mapping

### Imagen 4.0 Supported Sizes:
- **1K:** 1024x1024, 1024x768, 768x1024, 1280x768, 768x1280
- **2K:** 2048x2048, 2048x1536, 1536x2048

### Aspect Ratio Mapping:
- `1:1` → 1024x1024 (Instagram, Profile pics)
- `4:3` → 1024x768 (Blog inline, thumbnails)
- `3:4` → 768x1024 (Pinterest standard)
- `16:9` → 1280x768 (YouTube, Twitter, Hero)
- `9:16` → 768x1280 (Stories, Reels, TikTok)

**Note:** For exact sizes (1080x1080, 1200x675), generate at 1K and upscale, or use Imagen editing to resize.

---

## Social Media Template Tool Design

```python
@mcp.tool()
def generate_social_media_image(
    platform: str,  # "instagram_feed", "twitter_post", "linkedin_post"
    content_type: str,  # "product", "quote", "announcement", "behind_scenes"
    primary_text: str,  # Main headline/message
    description: str,  # Scene description
    style: str = "modern_minimal",  # "modern_minimal", "bold_vibrant", "elegant_luxury"
    brand_colors: Optional[List[str]] = None,  # ["#FF5733", "#3498DB"]
    include_text_overlay: bool = True
) -> Dict[str, Any]:
    """
    Generate platform-optimized social media images ready for posting.

    This tool:
    1. Selects correct dimensions for the platform
    2. Applies best practices for that platform's aesthetic
    3. Optionally adds text overlays (or returns base image for Canva)
    4. Returns BOTH local file AND base64 for direct upload

    No URL needed - image ready for direct platform upload!
    """
```

---

## Upload Patterns

### Pattern 1: Direct Upload (No URL Needed)
```python
# Generate image
result = generate_social_media_image(
    platform="instagram_feed",
    primary_text="Summer Vibes 🌊",
    description="bear in pool with sunglasses"
)

# Get local file or base64
image_path = result["local_path"]
image_base64 = result["base64_data"]

# Upload directly to Instagram API
instagram_api.create_post(
    image=image_base64,
    caption="Living the dream! #SummerVibes"
)
```

### Pattern 2: CMS Upload (No URL Needed)
```python
# Generate website hero image
result = generate_social_media_image(
    platform="website_hero",
    description="modern office workspace"
)

# Upload to WordPress
wordpress_api.upload_media(
    file=result["local_path"],
    post_id=123
)
```

### Pattern 3: Email (Needs URL)
```python
# Generate + upload to GCS for email use
result = generate_social_media_image(
    platform="email_header",
    description="product showcase",
    upload_to_cloud=True  # Enable GCS upload
)

# Use public URL in email HTML
email_html = f'<img src="{result["public_url"]}" />'
```

---

## Recommended Implementation

### Core Tools:
1. **`generate_social_media_image()`** - Platform-optimized generation
2. **`batch_generate_social_set()`** - Generate full campaign (all platforms)
3. **`optimize_for_platform()`** - Resize/crop existing image

### Return Format:
```python
{
    "success": true,
    "platform": "instagram_feed",
    "dimensions": "1080x1080",
    "local_path": "/path/to/image.png",
    "base64_data": "data:image/png;base64,iVBORw0KG...",  // For direct upload
    "file_size_mb": 1.2,
    "public_url": "https://storage.googleapis.com/...",  // Optional, if upload_to_cloud=True
    "best_practices": [
        "Image optimized for Instagram feed",
        "1:1 aspect ratio",
        "High contrast for mobile viewing"
    ]
}
```

---

## Canva API Alternative

Instead of Canva, generate **complete, ready-to-post images** with:
- Correct dimensions
- Platform-optimized composition
- Optional text overlays (using Imagen's text capabilities)
- Brand colors and style consistency

**Advantage over Canva:**
- Fully automated (no manual editing)
- Consistent AI-generated aesthetics
- Direct API integration
- No additional tool needed
