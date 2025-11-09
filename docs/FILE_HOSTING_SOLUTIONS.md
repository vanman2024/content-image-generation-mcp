# File Hosting Solutions for Generated Media

## The Problem

Generated images and videos are currently saved to the local filesystem:
- Images: `output/imagen_*.png`
- Videos: `output/veo_*.mp4`

**Issues:**
1. Files are not accessible via URL
2. Cannot be shared or embedded in websites/apps
3. When deployed to FastMCP Cloud, files are on the cloud server (not accessible)
4. No permanent storage - files may be lost on redeployment

## Solutions

### Option 1: Google Cloud Storage (Recommended)

**Pros:**
- Already have Google AI credentials
- Same billing account
- Industry standard, reliable
- Free tier: 5GB storage
- CDN-backed for fast global delivery
- Can generate signed URLs for temporary access

**Cost:**
- Storage: $0.026/GB/month (after 5GB free tier)
- Network: $0.12/GB (after 1GB free tier)
- For typical usage: ~$0.50-2.00/month

**Implementation:**
```python
from google.cloud import storage

def upload_to_gcs(file_path, bucket_name="your-bucket"):
    """Upload file to Google Cloud Storage and return public URL"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"generated/{file_path.name}")
    blob.upload_from_filename(str(file_path))

    # Make publicly accessible
    blob.make_public()

    return blob.public_url
```

**Setup Steps:**
1. Create GCS bucket: `gsutil mb gs://your-content-bucket`
2. Set public access: `gsutil iam ch allUsers:objectViewer gs://your-content-bucket`
3. Add `google-cloud-storage>=2.0.0` to requirements.txt
4. Use the same `GOOGLE_API_KEY` or create service account

---

### Option 2: Google AI File API (Simplest)

**Pros:**
- No additional setup needed (already using Google AI)
- Built into google-genai SDK
- **Files auto-deleted after 48 hours** (good for privacy)
- No storage costs

**Cons:**
- Temporary URLs only (48 hours)
- Not suitable for permanent content library

**Implementation:**
```python
# Upload file to Google AI File API
uploaded_file = genai_client.files.upload(
    path=str(filepath),
    display_name=filepath.name
)

# Get shareable URI
file_uri = uploaded_file.uri  # Valid for 48 hours

return {
    "file_uri": file_uri,
    "expires_at": uploaded_file.expiration_time,
    "download_url": f"https://generativelanguage.googleapis.com/v1beta/files/{uploaded_file.name}"
}
```

---

### Option 3: Supabase Storage

**Pros:**
- Easy to use
- Built-in authentication and RLS
- Generous free tier (1GB storage)
- CDN-backed
- Can integrate with user accounts

**Cost:**
- Free tier: 1GB storage, 2GB bandwidth
- Pro: $25/month (100GB storage, 200GB bandwidth)

**Implementation:**
```python
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def upload_to_supabase(file_path, bucket="generated-content"):
    with open(file_path, 'rb') as f:
        response = supabase.storage.from_(bucket).upload(
            f"images/{file_path.name}",
            f
        )

    # Get public URL
    url = supabase.storage.from_(bucket).get_public_url(f"images/{file_path.name}")
    return url
```

---

### Option 4: Cloudflare R2 (Cost-Effective)

**Pros:**
- Zero egress fees (free bandwidth!)
- S3-compatible API
- Very affordable
- Free tier: 10GB storage/month

**Cost:**
- Storage: $0.015/GB/month (after 10GB free tier)
- **No bandwidth charges**
- Cheapest for high-traffic scenarios

**Implementation:**
```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
)

s3.upload_file(
    str(file_path),
    'bucket-name',
    f'generated/{file_path.name}'
)

public_url = f"https://pub-{bucket_id}.r2.dev/generated/{file_path.name}"
```

---

### Option 5: Base64 Embedding (Images Only)

**Pros:**
- No external service needed
- Works immediately
- Good for small images in API responses

**Cons:**
- Large response payloads (4/3 size increase)
- Not suitable for videos
- Not suitable for multiple/large images

**Implementation:**
```python
import base64

with open(filepath, 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')

return {
    "image_data": f"data:image/png;base64,{encoded}",
    "size_kb": len(encoded) / 1024
}
```

---

## Recommendation

**For immediate use:**
- **Option 2 (Google AI File API)** - Already integrated, zero setup, works now

**For production:**
- **Option 1 (Google Cloud Storage)** - Most reliable, same billing, industry standard
- Alternative: **Option 4 (Cloudflare R2)** - If you need high bandwidth at low cost

## Implementation Priority

1. **Phase 1:** Add Google AI File API support (immediate, 48-hour expiry)
2. **Phase 2:** Add Google Cloud Storage support (permanent hosting)
3. **Phase 3:** Add optional Supabase/R2 support (user choice)

---

## Code Example: Dual Return (Local + Cloud)

```python
@mcp.tool()
def generate_image_imagen3(...) -> Dict[str, Any]:
    # Generate image
    response = genai_client.models.generate_images(...)

    # Save locally
    local_path = OUTPUT_DIR / filename
    response.generated_images[0].image.save(str(local_path))

    # Upload to Google AI File API (48-hour hosting)
    uploaded_file = genai_client.files.upload(
        path=str(local_path),
        display_name=filename
    )

    return {
        "success": True,
        "local_path": str(local_path),
        "cloud_url": uploaded_file.uri,
        "expires_at": uploaded_file.expiration_time.isoformat(),
        "note": "Cloud URL valid for 48 hours"
    }
```

This gives users both local files AND shareable URLs!
