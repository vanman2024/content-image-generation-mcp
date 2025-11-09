#!/usr/bin/env python3
"""
Test the bear in pool scenario with actual API calls
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import Google Gen AI SDK
from google import genai
from google.genai import types

# Configuration
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("🚀 BEAR IN POOL - COMPLETE TEST\n")
print("=" * 80)

# Test 1: Generate Image
print("\n🖼️  STEP 1: GENERATING IMAGE WITH IMAGEN 4.0\n")

image_prompt = """Photorealistic image of a relaxed bear wearing stylish sunglasses
sitting in a crystal-clear backyard swimming pool, casually holding a glass of
Coca-Cola with ice. The bear looks completely content and comfortable, lounging in
the water on a bright sunny day. Professional photography, high detail, 16:9 aspect
ratio, vibrant colors."""

print(f"📝 Prompt: {image_prompt[:80]}...")
print("\n⏳ Calling Imagen 4.0 API...")

try:
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=image_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            image_size="1K",
            aspect_ratio="16:9",
            person_generation="allow_adult",
        ),
    )

    # Save image
    filename = f"bear_pool_imagen.png"
    filepath = OUTPUT_DIR / filename
    response.generated_images[0].image.save(str(filepath))

    print(f"\n✅ IMAGE GENERATED!")
    print(f"📁 Saved to: {filepath.absolute()}")
    print(f"💰 Cost: $0.04 (1K resolution)")

except Exception as e:
    print(f"\n❌ IMAGE GENERATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Generate Video
print("\n" + "=" * 80)
print("\n🎬 STEP 2: GENERATING VIDEO WITH VEO 3.1\n")

video_prompt = """A photorealistic 8-second video: A bear wearing sunglasses relaxes
in a backyard swimming pool, holding a glass of Coca-Cola with ice. Suddenly, a person
appears at the pool edge and throws their hands up in shock and surprise, mouth wide
open, clearly exclaiming "Oh my God, there's a bear in the pool!" The bear casually
takes a sip of the Coke, completely unbothered. Bright sunny day, natural lighting,
professional cinematography, realistic motion."""

print(f"📝 Prompt: {video_prompt[:80]}...")
print("\n⏳ Calling Veo 3.1 API...")
print("   ⚠️  This will take 2-6 minutes - please be patient!")

try:
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=video_prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",
            resolution="720p",
            duration_seconds=8,
            number_of_videos=1,
        ),
    )

    # Poll until done
    waited = 0
    while not operation.done and waited < 360:
        time.sleep(10)
        waited += 10
        operation = client.operations.get(operation)
        if waited % 30 == 0:
            print(f"   ... {waited}s elapsed")

    if not operation.done:
        print("\n❌ VIDEO GENERATION TIMED OUT")
        sys.exit(1)

    # Save video
    generated_video = operation.response.generated_videos[0]
    filename = f"bear_pool_veo.mp4"
    filepath = OUTPUT_DIR / filename

    client.files.download(file=generated_video.video)
    generated_video.video.save(str(filepath))

    print(f"\n✅ VIDEO GENERATED!")
    print(f"📁 Saved to: {filepath.absolute()}")
    print(f"⏱️  Duration: 8 seconds")
    print(f"🎵 Audio: Native generation included")
    print(f"💰 Cost: $6.00 (8s × $0.75/s)")

except Exception as e:
    print(f"\n❌ VIDEO GENERATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Generate Social Post
print("\n" + "=" * 80)
print("\n📱 STEP 3: GENERATING SOCIAL MEDIA POST WITH GEMINI\n")

content_prompt = """Generate a fun, casual social media post about this scenario:
A bear relaxing in a swimming pool with sunglasses and a Coke - complete unexpected
summer vibes. Make it engaging and include relevant hashtags."""

print("⏳ Calling Gemini 2.0 Flash...")

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=content_prompt,
    )

    content = response.text

    print(f"\n✅ SOCIAL POST GENERATED!")
    print("\n" + "=" * 80)
    print(content)
    print("=" * 80)
    print(f"\n💰 Cost: ~$0.0003")

except Exception as e:
    print(f"\n❌ CONTENT GENERATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Final Summary
print("\n" + "=" * 80)
print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
print(f"\n📂 Generated files in: {OUTPUT_DIR.absolute()}")
print(f"   - Image: bear_pool_imagen.png")
print(f"   - Video: bear_pool_veo.mp4")
print(f"\n💰 Total estimated cost: $6.04")
print("\nYou now have a complete marketing campaign!")
