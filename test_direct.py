#!/usr/bin/env python3
"""
Direct test of Google Gemini API for image and video generation
"""

import os
import base64
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Output directory
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_image_generation():
    """Test Imagen 3 image generation"""
    print("=" * 80)
    print("🖼️  TESTING IMAGE GENERATION (Imagen 3)")
    print("=" * 80)

    prompt = """Photorealistic image of a relaxed bear wearing sunglasses sitting
    in a backyard swimming pool, holding a glass of Coca-Cola with ice.
    The bear looks content and comfortable, lounging in the crystal clear water.
    Bright sunny day, professional photography, high detail."""

    print(f"\n📝 Prompt: {prompt[:80]}...")
    print("\n⏳ Calling Gemini API for Imagen 3...")

    try:
        # Initialize model
        model = genai.GenerativeModel("imagen-3.0-generate-002")

        # Generate image
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9"
        )

        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bear_pool_{timestamp}.png"
        filepath = OUTPUT_DIR / filename

        # Decode and save
        image_data = base64.b64decode(response.images[0].data)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        print(f"\n✅ IMAGE GENERATED SUCCESSFULLY!")
        print(f"📁 Saved to: {filepath.absolute()}")
        print(f"💰 Estimated cost: $0.02 (1K image)")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_generation():
    """Test Veo 3 video generation"""
    print("\n" + "=" * 80)
    print("🎬 TESTING VIDEO GENERATION (Veo 3)")
    print("=" * 80)

    prompt = """A photorealistic video: A bear wearing sunglasses relaxes in a
    backyard swimming pool, holding a Coca-Cola. Suddenly a person appears at the
    pool edge, throws their hands up in shock, mouth open. The bear casually takes
    a sip, unbothered. Sunny day, natural lighting, realistic motion.
    Audio: Person exclaims "Oh my God, there's a bear in the pool!" """

    print(f"\n📝 Prompt: {prompt[:80]}...")
    print("\n⏳ Calling Gemini API for Veo 3...")
    print("   ⚠️  This takes 2-6 minutes - please wait...")

    try:
        # Start video generation
        operation = genai.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=prompt,
            config={
                "aspect_ratio": "16:9",
                "resolution": "720p",
                "duration_seconds": "8"
            }
        )

        print(f"\n⏱️  Operation started: {operation.name}")
        print("   Polling for completion...")

        # Poll until complete
        max_wait = 360  # 6 minutes
        waited = 0
        while not operation.done and waited < max_wait:
            time.sleep(10)
            waited += 10
            operation = genai.operations.get(operation.name)
            print(f"   ... {waited}s elapsed")

        if not operation.done:
            print(f"\n❌ TIMEOUT: Video generation took longer than {max_wait}s")
            return False

        # Save video
        video_data = operation.response.generated_videos[0].video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bear_pool_video_{timestamp}.mp4"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'wb') as f:
            f.write(video_data)

        print(f"\n✅ VIDEO GENERATED SUCCESSFULLY!")
        print(f"📁 Saved to: {filepath.absolute()}")
        print(f"⏱️  Duration: 8 seconds")
        print(f"📺 Resolution: 720p")
        print(f"🎵 Audio: Native generation included")
        print(f"💰 Estimated cost: $6.00 (8s × $0.75/s)")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_content_generation():
    """Test Gemini content generation"""
    print("\n" + "=" * 80)
    print("📱 TESTING CONTENT GENERATION (Gemini 2.5 Flash)")
    print("=" * 80)

    topic = """A bear relaxing in a swimming pool with sunglasses and a Coke -
    unexpected summer vibes"""

    prompt = f"""Generate a casual, engaging social media post about: {topic}

Tone: casual and fun
Length: 3-5 sentences or 1 paragraph
Include relevant hashtags at the end.

Make it compelling, engaging, and ready to use for marketing."""

    print(f"\n📝 Topic: {topic[:80]}...")
    print("\n⏳ Calling Gemini API...")

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        content = response.text

        print(f"\n✅ CONTENT GENERATED SUCCESSFULLY!")
        print("\n" + "=" * 80)
        print(content)
        print("=" * 80)
        print(f"\n💰 Estimated cost: $0.0003 (~500 tokens)")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🚀 DIRECT GEMINI API TEST - BEAR IN POOL SCENARIO\n")

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found")
        return

    print("✅ API Key configured")

    # Run tests
    results = []

    # Test 1: Image
    results.append(("Image Generation", test_image_generation()))

    # Test 2: Video
    results.append(("Video Generation", test_video_generation()))

    # Test 3: Content
    results.append(("Content Generation", test_content_generation()))

    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")

    if all(r[1] for r in results):
        print("\n🎉 ALL TESTS PASSED!")
        print(f"\n📂 Check output directory: {OUTPUT_DIR.absolute()}")
    else:
        print("\n⚠️  SOME TESTS FAILED")


if __name__ == "__main__":
    main()
