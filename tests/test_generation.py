#!/usr/bin/env python3
"""
Test script for content-image-generation-mcp server
Tests actual image generation, video generation, and content creation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the server module
from server import (
    generate_image_imagen3,
    generate_video_veo3,
    generate_marketing_content
)

def test_image_generation():
    """Test Imagen 3 image generation with bear in pool"""
    print("=" * 80)
    print("🖼️  TESTING IMAGE GENERATION")
    print("=" * 80)

    prompt = """A photorealistic image of a bear wearing sunglasses sitting relaxed
    in a backyard swimming pool, holding a glass of Coca-Cola with ice. The bear
    looks content and comfortable, lounging in the water. Bright sunny day,
    crystal clear pool water, professional photography, high detail, 8k quality."""

    print(f"\n📝 Prompt: {prompt[:100]}...")
    print("\n⏳ Generating image with Imagen 3...")

    result = generate_image_imagen3(
        prompt=prompt,
        aspect_ratio="16:9",
        image_size="1K",
        model_version="imagen-3.0"
    )

    if result.get("success"):
        print("\n✅ IMAGE GENERATION SUCCESSFUL!")
        for img in result.get("images", []):
            print(f"\n📁 Saved to: {img['image_path']}")
            print(f"   Filename: {img['filename']}")
        print(f"\n💰 Cost: ${result.get('estimated_cost_usd')}")
        print(f"📏 Aspect Ratio: {result.get('aspect_ratio')}")
        print(f"🎨 Model: {result.get('model')}")
    else:
        print(f"\n❌ IMAGE GENERATION FAILED: {result.get('error')}")
        return False

    return True


def test_video_generation():
    """Test Veo 3 video generation with bear in pool scene"""
    print("\n" + "=" * 80)
    print("🎬 TESTING VIDEO GENERATION")
    print("=" * 80)

    prompt = """A photorealistic video of a bear wearing sunglasses relaxing in a
    backyard swimming pool, holding a Coca-Cola. A person suddenly appears at the
    pool edge, throws their hands up in shock and surprise, mouth open, clearly
    saying "Oh my God, there's a bear in the pool!" The bear casually takes a sip
    of the Coke, completely unbothered. Bright sunny day, professional cinematography,
    natural lighting, realistic motion."""

    print(f"\n📝 Prompt: {prompt[:100]}...")
    print("\n⏳ Generating 8-second video with Veo 3...")
    print("   (This may take 2-6 minutes due to AI processing)")

    result = generate_video_veo3(
        prompt=prompt,
        duration_seconds=8,
        resolution="720p",
        aspect_ratio="16:9"
    )

    if result.get("success"):
        print("\n✅ VIDEO GENERATION SUCCESSFUL!")
        print(f"\n📁 Saved to: {result.get('video_path')}")
        print(f"   Filename: {result.get('filename')}")
        print(f"\n⏱️  Duration: {result.get('duration_seconds')}s")
        print(f"📺 Resolution: {result.get('resolution')}")
        print(f"🎵 Has Audio: {result.get('has_audio')}")
        print(f"💰 Cost: ${result.get('estimated_cost_usd')}")
        print(f"🎨 Model: {result.get('model')}")
    else:
        print(f"\n❌ VIDEO GENERATION FAILED: {result.get('error')}")
        return False

    return True


def test_content_generation():
    """Test social media post generation about the bear"""
    print("\n" + "=" * 80)
    print("📱 TESTING CONTENT GENERATION")
    print("=" * 80)

    print("\n⏳ Generating social media post with Gemini 2.5 Flash...")

    result = generate_marketing_content(
        content_type="social_post",
        topic="A bear relaxing in a swimming pool with sunglasses and a Coke - unexpected summer vibes",
        tone="casual",
        length="medium",
        model="gemini",
        include_hashtags=True
    )

    if result.get("success"):
        print("\n✅ CONTENT GENERATION SUCCESSFUL!")
        print("\n" + "=" * 80)
        print(result.get("content"))
        print("=" * 80)
        print(f"\n📊 Stats:")
        print(f"   Model: {result.get('model_used')}")
        print(f"   Tokens: {result.get('tokens_used')}")
        print(f"   Cost: ${result.get('estimated_cost_usd')}")
    else:
        print(f"\n❌ CONTENT GENERATION FAILED: {result.get('error')}")
        return False

    return True


def main():
    """Run all tests"""
    print("\n🚀 CONTENT & IMAGE GENERATION MCP SERVER - LIVE TEST\n")

    # Check environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set GOOGLE_API_KEY in .env file")
        sys.exit(1)

    print("✅ Environment configured")
    print(f"   Google API Key: {os.getenv('GOOGLE_API_KEY')[:20]}...")

    # Run tests
    results = []

    # Test 1: Image Generation
    results.append(("Image Generation", test_image_generation()))

    # Test 2: Video Generation
    results.append(("Video Generation", test_video_generation()))

    # Test 3: Content Generation
    results.append(("Content Generation", test_content_generation()))

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📂 Check the 'output' directory for generated files:")
        print("   - Images: output/imagen_*.png")
        print("   - Videos: output/veo3_*.mp4")
    else:
        print("\n⚠️  SOME TESTS FAILED - Check errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()
