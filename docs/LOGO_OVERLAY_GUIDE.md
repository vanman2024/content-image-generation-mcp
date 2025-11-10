# Logo Overlay on Generated Images

## The Problem

**Imagen 4 cannot reliably place logos:**
- Max 25 characters of text
- Can't control exact positioning
- Can't guarantee logo appearance/quality
- "Occasional variations" in placement

**Solution:** Generate clean image, overlay logo with Pillow (PIL)

---

## Architecture

```
┌─────────────────────────────────────┐
│ Step 1: Generate Base Image         │
│ MCP Server (Imagen 4)               │
│                                     │
│ → Clean professional photo          │
│ → No logo, no text                  │
│ → Returns base64 data               │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 2: Overlay Logo                │
│ Python Script (Pillow)              │
│                                     │
│ → Decode base64 image               │
│ → Load brand logo (PNG with alpha) │
│ → Composite logo at position        │
│ → Encode back to base64             │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ Step 3: Store in Airtable           │
│ Final image with logo               │
└─────────────────────────────────────┘
```

---

## Implementation Options

### Option 1: Standalone Python Script (Simplest)

**File:** `logo_overlay.py`

```python
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import os


def overlay_logo_on_image(
    base_image_base64: str,
    logo_path: str,
    position: str = "bottom-right",
    logo_size: tuple = (150, 150),
    padding: int = 20,
    opacity: float = 0.9
) -> str:
    """
    Overlay a logo on a base64-encoded image.

    Args:
        base_image_base64: Base64 string from MCP server (with or without data:image prefix)
        logo_path: Path to logo PNG file (must have transparency/alpha channel)
        position: "top-left", "top-right", "bottom-left", "bottom-right", "center"
        logo_size: (width, height) to resize logo
        padding: Pixels from edge
        opacity: Logo opacity (0.0 to 1.0)

    Returns:
        Base64-encoded image with logo overlay
    """

    # Decode base image from base64
    if "base64," in base_image_base64:
        base_image_base64 = base_image_base64.split("base64,")[1]

    image_data = base64.b64decode(base_image_base64)
    base_image = Image.open(BytesIO(image_data)).convert("RGBA")

    # Load and resize logo
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

    # Adjust logo opacity
    if opacity < 1.0:
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        logo.putalpha(alpha)

    # Calculate position
    base_width, base_height = base_image.size
    logo_width, logo_height = logo.size

    positions = {
        "top-left": (padding, padding),
        "top-right": (base_width - logo_width - padding, padding),
        "bottom-left": (padding, base_height - logo_height - padding),
        "bottom-right": (base_width - logo_width - padding, base_height - logo_height - padding),
        "center": ((base_width - logo_width) // 2, (base_height - logo_height) // 2)
    }

    logo_position = positions.get(position, positions["bottom-right"])

    # Create composite
    result = base_image.copy()
    result.paste(logo, logo_position, logo)  # Third param is mask for transparency

    # Convert back to RGB for JPEG compatibility (optional)
    result_rgb = Image.new("RGB", result.size, (255, 255, 255))
    result_rgb.paste(result, mask=result.split()[3])

    # Encode to base64
    buffer = BytesIO()
    result_rgb.save(buffer, format="PNG", quality=95)

    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"


# Example usage
if __name__ == "__main__":
    # Assume you have base64 data from MCP server
    base_image = "data:image/png;base64,iVBORw0KGgo..."  # From MCP server

    # Logo file (PNG with transparency)
    logo_file = "challenge-red-seal-logo.png"

    # Overlay logo
    final_image = overlay_logo_on_image(
        base_image_base64=base_image,
        logo_path=logo_file,
        position="bottom-right",
        logo_size=(200, 200),
        padding=30,
        opacity=0.85
    )

    print(f"Final image size: {len(final_image)} bytes")

    # Save to file for preview
    image_data = base64.b64decode(final_image.split(',')[1])
    with open("final_with_logo.png", "wb") as f:
        f.write(image_data)
```

**Dependencies:**
```bash
pip install Pillow
```

---

### Option 2: FastAPI Service (For Production)

**File:** `logo_overlay_service.py`

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
import base64
from io import BytesIO
import os

app = FastAPI(title="Logo Overlay Service")


class LogoOverlayRequest(BaseModel):
    base_image_base64: str
    brand_name: str  # "Challenge Red Seal", "Skill Trace", etc.
    position: str = "bottom-right"
    logo_size: tuple[int, int] = (150, 150)
    padding: int = 20
    opacity: float = 0.9


class LogoOverlayResponse(BaseModel):
    success: bool
    image_with_logo_base64: str
    original_size_kb: float
    final_size_kb: float


# Brand logo mappings
BRAND_LOGOS = {
    "Challenge Red Seal": "logos/challenge-red-seal.png",
    "Skill Trace": "logos/skill-trace.png",
    "Collars Employment Group": "logos/collars-employment.png",
    "Job Hub": "logos/job-hub.png",
}


@app.post("/overlay-logo", response_model=LogoOverlayResponse)
async def overlay_logo(request: LogoOverlayRequest):
    """
    Overlay brand logo on generated image.

    Example:
        POST /overlay-logo
        {
          "base_image_base64": "data:image/png;base64,iVBORw0KGgo...",
          "brand_name": "Challenge Red Seal",
          "position": "bottom-right",
          "logo_size": [200, 200],
          "opacity": 0.85
        }
    """
    try:
        # Get logo path for brand
        logo_path = BRAND_LOGOS.get(request.brand_name)
        if not logo_path or not os.path.exists(logo_path):
            raise HTTPException(status_code=404, detail=f"Logo not found for brand: {request.brand_name}")

        # Decode base image
        if "base64," in request.base_image_base64:
            base64_data = request.base_image_base64.split("base64,")[1]
        else:
            base64_data = request.base_image_base64

        image_data = base64.b64decode(base64_data)
        original_size_kb = len(image_data) / 1024

        base_image = Image.open(BytesIO(image_data)).convert("RGBA")

        # Load and resize logo
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize(request.logo_size, Image.Resampling.LANCZOS)

        # Adjust opacity
        if request.opacity < 1.0:
            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: int(p * request.opacity))
            logo.putalpha(alpha)

        # Calculate position
        base_width, base_height = base_image.size
        logo_width, logo_height = logo.size

        positions = {
            "top-left": (request.padding, request.padding),
            "top-right": (base_width - logo_width - request.padding, request.padding),
            "bottom-left": (request.padding, base_height - logo_height - request.padding),
            "bottom-right": (base_width - logo_width - request.padding, base_height - logo_height - request.padding),
            "center": ((base_width - logo_width) // 2, (base_height - logo_height) // 2)
        }

        logo_position = positions.get(request.position, positions["bottom-right"])

        # Composite
        result = base_image.copy()
        result.paste(logo, logo_position, logo)

        # Convert to RGB
        result_rgb = Image.new("RGB", result.size, (255, 255, 255))
        result_rgb.paste(result, mask=result.split()[3])

        # Encode
        buffer = BytesIO()
        result_rgb.save(buffer, format="PNG", quality=95)

        final_data = buffer.getvalue()
        final_size_kb = len(final_data) / 1024

        encoded = base64.b64encode(final_data).decode('utf-8')

        return LogoOverlayResponse(
            success=True,
            image_with_logo_base64=f"data:image/png;base64,{encoded}",
            original_size_kb=round(original_size_kb, 2),
            final_size_kb=round(final_size_kb, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "logo-overlay"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Run:**
```bash
pip install fastapi uvicorn pillow
uvicorn logo_overlay_service:app --reload --port 8001
```

---

### Option 3: Add to MCP Server (FUTURE - Not Recommended Now)

**Why not add to MCP server:**
- Different responsibility (image generation vs image processing)
- Need to manage logo files
- Increases deployment complexity
- Better as separate service

**If you really want it in MCP server later:**
```python
@mcp.tool()
def overlay_brand_logo(
    base_image_base64: str,
    brand_name: str,
    position: str = "bottom-right"
) -> Dict[str, Any]:
    """Overlay brand logo on generated image."""
    # Same logic as above
```

---

## Integration with Make.com Workflow

### Updated Workflow with Logo Overlay

```
Step 1: Query Airtable Brands table
  ↓ Get brand context + logo URL
Step 2: Call MCP Server
  ↓ Generate clean image (no logo)
Step 3: Call Logo Overlay Service
  ↓ Add brand logo to image
Step 4: Create Airtable Assets record
  ↓ Store final image with logo
Step 5: Create Social Posts Queue
  ↓ Ready to post!
```

### Make.com Modules

```javascript
// Module 1: Airtable > Get Brand
{
  "base": "apprJV9UhYEDNL6J7",
  "table": "Brands",
  "record_id": "..."
}
// Returns: brand_name, description, logo_url

// Module 2: HTTP > Call MCP Server
POST https://content.fastmcp.app/mcp
{
  "tool": "batch_generate_campaign",
  "params": {
    "campaign_brief": "...",
    "platforms": ["instagram_feed"],
    "image_style": "photorealistic"
  }
}
// Returns: base64_image (no logo)

// Module 3: HTTP > Call Logo Overlay Service
POST http://your-logo-service.com/overlay-logo
{
  "base_image_base64": "{{2.platforms[0].image.base64_data}}",
  "brand_name": "{{1.brand_name}}",
  "position": "bottom-right",
  "logo_size": [200, 200],
  "opacity": 0.85
}
// Returns: image_with_logo_base64

// Module 4: Airtable > Create Asset
{
  "base": "apprJV9UhYEDNL6J7",
  "table": "Assets",
  "record": {
    "Base64 Data": "{{3.image_with_logo_base64}}",
    "Has Logo": true,
    "Brand": ["{{1.id}}"]
  }
}
```

---

## Logo File Requirements

### Best Practices

1. **Format:** PNG with alpha channel (transparency)
2. **Size:** At least 500x500px (will be resized)
3. **Background:** Transparent
4. **Color:** Full color or white (for dark backgrounds)
5. **File naming:** `brand-name-logo.png` (e.g., `challenge-red-seal-logo.png`)

### Store Logos

**Option A: Local files in service**
```
/logos/
  challenge-red-seal.png
  skill-trace.png
  collars-employment.png
  job-hub.png
```

**Option B: Airtable Attachments field**
- Add "Logo File" attachment field to Brands table
- Download logo URL in Make.com
- Pass logo data to overlay service

**Option C: Cloud storage (Google Cloud Storage, S3)**
- Upload logos to cloud bucket
- Reference by URL
- Download and cache in overlay service

---

## Cost & Performance

### Standalone Script
- **Cost:** Free (runs locally)
- **Speed:** ~0.5 seconds per image
- **Scaling:** Run in Make.com Custom Code module

### FastAPI Service
- **Cost:** ~$5/month (small VPS) or serverless
- **Speed:** ~0.3 seconds per image
- **Scaling:** Deploy on Railway, Render, DigitalOcean

### Processing Time
```
MCP Server (generate image): ~5-10 seconds
Logo overlay: ~0.3-0.5 seconds
Total: ~5-11 seconds end-to-end
```

---

## Quick Start: Test Logo Overlay Now

### 1. Install Pillow
```bash
pip install Pillow
```

### 2. Get Challenge Red Seal Logo
Save as `challenge-red-seal-logo.png` (PNG with transparency)

### 3. Test Script
```python
from PIL import Image
import base64
from io import BytesIO

# Your base64 image from MCP server
base_image_b64 = "data:image/png;base64,iVBORw0KGgo..."  # From previous test

# Decode
img_data = base64.b64decode(base_image_b64.split(',')[1])
base = Image.open(BytesIO(img_data)).convert("RGBA")

# Load logo
logo = Image.open("challenge-red-seal-logo.png").convert("RGBA")
logo = logo.resize((150, 150), Image.Resampling.LANCZOS)

# Position: bottom-right with 20px padding
x = base.width - logo.width - 20
y = base.height - logo.height - 20

# Overlay
base.paste(logo, (x, y), logo)

# Save
base.save("test_with_logo.png")
print("✅ Logo overlay complete! Check test_with_logo.png")
```

---

## Recommendations

### For Now (Testing Phase)
1. **Use standalone Python script**
2. **Manual overlay** for first few campaigns
3. **Validate logo positioning** looks good
4. **Test with different platforms** (Instagram square vs LinkedIn horizontal)

### For Production (After Validation)
1. **Build FastAPI logo overlay service**
2. **Deploy to Railway/DigitalOcean**
3. **Integrate with Make.com workflow**
4. **Store logos in Brands table** (Attachments field)
5. **Add to automation pipeline**

### Not Recommended
- ❌ Adding logo overlay to MCP server (wrong separation of concerns)
- ❌ Using Imagen to generate logos (unreliable)
- ❌ Hardcoding logo positions (use brand-specific settings)

---

## Next Steps

1. **Get Challenge Red Seal logo PNG** (with transparency)
2. **Test standalone script** with one generated image
3. **Validate positioning** (bottom-right? top-left? center?)
4. **Build FastAPI service** (if you like the results)
5. **Add to Make.com workflow** (Module 3 after image generation)

Want me to help you test the logo overlay script right now?
