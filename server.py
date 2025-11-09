"""
FastMCP Content & Image Generation Server

AI-powered content and image generation with:
- Google Imagen 3/4 image generation
- Google Veo 2/3 video generation
- Claude/Gemini content generation
- Cost estimation and tracking
"""

import os
import json
import base64
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP
from dotenv import load_dotenv

# Anthropic Claude
from anthropic import Anthropic

# Google Gen AI SDK (New unified SDK for Imagen, Veo, and Gemini)
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure logging for production
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name=os.getenv("MCP_SERVER_NAME", "Content & Image Generation"))

# Log startup
logger.info(f"Starting {mcp.name} server")

# Configuration
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Google Gen AI Client
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    logger.error("GOOGLE_API_KEY environment variable is required")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

try:
    genai_client = genai.Client(api_key=google_api_key)
    logger.info("Google Gen AI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Gen AI client: {e}")
    raise

# Initialize Anthropic
anthropic_client = None
if os.getenv("ANTHROPIC_API_KEY"):
    try:
        anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        logger.info("Anthropic client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Anthropic client: {e}")
else:
    logger.info("Anthropic API key not provided - Claude content generation will be unavailable")


# Pricing Constants (USD per unit) - Updated from official docs
PRICING = {
    # Imagen pricing (per image)
    "imagen3_1k": 0.02,  # 1K image
    "imagen3_2k": 0.04,  # 2K image
    "imagen4_1k": 0.04,  # 1K image
    "imagen4_2k": 0.08,  # 2K image
    # Veo pricing (per second of video)
    "veo2": 0.40,  # Veo 2
    "veo3": 0.75,  # Veo 3 Standard
    "veo3_fast": 0.40,  # Veo 3 Fast
    # Content generation (per 1K tokens)
    "claude_sonnet": 0.003,
    "gemini_flash": 0.0005,
}


@mcp.tool()
def health_check() -> Dict[str, Any]:
    """
    Check server health and API connectivity.

    Returns:
        Dictionary with health status and available services
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "google_genai": bool(google_api_key),
                "anthropic": bool(anthropic_client),
            },
            "output_directory": str(OUTPUT_DIR.absolute()),
            "output_directory_writable": OUTPUT_DIR.is_dir() and os.access(OUTPUT_DIR, os.W_OK)
        }

        logger.info("Health check passed")
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool()
def generate_image_imagen3(
    prompt: str,
    negative_prompt: Optional[str] = None,
    aspect_ratio: str = "1:1",
    number_of_images: int = 1,
    image_size: str = "1K",
    output_format: str = "png",
    model_version: str = "imagen-4.0",
) -> Dict[str, Any]:
    """
    Generate marketing images using Google Imagen via Gemini API.

    Args:
        prompt: Detailed description of the image to generate
        negative_prompt: What to avoid in the image
        aspect_ratio: Image aspect ratio - "1:1", "3:4", "4:3", "9:16", "16:9"
        number_of_images: Number of images to generate (1-4)
        image_size: Image size - "1K" or "2K"
        output_format: Output format (png, jpeg)
        model_version: Model - "imagen-3.0", "imagen-4.0", "imagen-4.0-ultra", "imagen-4.0-fast"

    Returns:
        Dictionary with image paths, metadata, and estimated cost
    """
    logger.info(f"Generating {number_of_images} image(s) with {model_version}: {prompt[:50]}...")
    try:
        # Validate
        if number_of_images < 1 or number_of_images > 4:
            number_of_images = 1

        # Map to actual model IDs
        model_map = {
            "imagen-3.0": "imagen-3.0-generate-002",
            "imagen-4.0": "imagen-4.0-generate-001",
            "imagen-4.0-ultra": "imagen-4.0-ultra-generate-001",
            "imagen-4.0-fast": "imagen-4.0-fast-generate-001"
        }
        model_id = model_map.get(model_version, "imagen-4.0-generate-001")

        # Generate images using new google-genai SDK
        response = genai_client.models.generate_images(
            model=model_id,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=number_of_images,
                image_size=image_size if image_size in ["1K", "2K"] else "1K",
                aspect_ratio=aspect_ratio,
                person_generation="allow_adult",
            ),
        )

        # Save all images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_images = []

        for i, generated_image in enumerate(response.generated_images):
            filename = f"imagen_{model_version}_{timestamp}_{i+1}.{output_format}"
            filepath = OUTPUT_DIR / filename

            # Save image
            generated_image.image.save(str(filepath))

            saved_images.append({
                "image_path": str(filepath.absolute()),
                "filename": filename
            })

        # Calculate cost
        if "4.0" in model_version:
            if "ultra" in model_version.lower():
                cost_per_image = 0.12 if image_size == "2K" else 0.08
            else:
                cost_per_image = 0.04 if image_size == "1K" else 0.08
        else:  # Imagen 3.0
            cost_per_image = 0.02 if image_size == "1K" else 0.04

        total_cost = cost_per_image * number_of_images

        logger.info(f"Successfully generated {number_of_images} image(s) with {model_version} (cost: ${total_cost:.4f})")
        return {
            "success": True,
            "images": saved_images,
            "model": model_id,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
            "number_of_images": number_of_images,
            "estimated_cost_usd": round(total_cost, 4),
            "timestamp": timestamp,
            "note": "Images include SynthID watermarking"
        }

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "model": model_version
        }


@mcp.tool()
def batch_generate_images(
    prompts: List[str],
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    model_version: str = "imagen-3.0",
) -> Dict[str, Any]:
    """
    Generate multiple marketing images in batch.

    Args:
        prompts: List of image prompts
        aspect_ratio: Image aspect ratio for all images
        image_size: Image size - "1K" or "2K"
        model_version: Model to use - "imagen-3.0" or "imagen-4.0"

    Returns:
        Dictionary with list of generated images and total cost
    """
    results = []
    total_cost = 0.0
    successful = 0
    failed = 0

    for i, prompt in enumerate(prompts, 1):
        result = generate_image_imagen3(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            model_version=model_version
        )

        results.append({
            "index": i,
            "prompt": prompt,
            **result
        })

        if result.get("success"):
            successful += 1
            total_cost += result.get("estimated_cost_usd", 0)
        else:
            failed += 1

    return {
        "success": True,
        "total_images": len(prompts),
        "successful": successful,
        "failed": failed,
        "results": results,
        "total_cost_usd": round(total_cost, 4),
        "model_version": model_version
    }


@mcp.tool()
def generate_video_veo3(
    prompt: str,
    duration_seconds: int = 8,
    resolution: str = "720p",
    aspect_ratio: str = "16:9",
    negative_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate marketing videos with NATIVE AUDIO using Google Veo 3 via Gemini API.

    🔊 AUDIO GENERATION: Veo 3.1 automatically generates audio including:
    - Dialogue: Use quotes in prompt: "Oh my God, there's a bear!" she exclaimed
    - Sound effects: Describe explicitly: water splashing, bear grunting, glass clinking
    - Ambient sounds: poolside ambiance, summer afternoon sounds, birds chirping

    ⚠️ COST WARNING: Video generation is expensive!
    - 4 seconds = $3.00
    - 6 seconds = $4.50
    - 8 seconds = $6.00

    Consider using Veo Fast models for 50% cost reduction.

    Args:
        prompt: Detailed description with audio cues (dialogue in quotes, sound effects described)
        duration_seconds: Video duration - 4, 6, or 8 seconds (default: 8)
        resolution: Video resolution - "720p" or "1080p" (1080p limited to 8s)
        aspect_ratio: Video aspect ratio - "16:9" or "9:16" (default: "16:9")
        negative_prompt: Elements to exclude from the video

    Returns:
        Dictionary with video path, metadata, and estimated cost

    Note: Generated videos are saved locally. For sharing/embedding, consider integrating
    cloud storage (Google Cloud Storage, Supabase Storage, etc.) to get public URLs.
    """
    try:
        import time

        # Validate parameters
        if duration_seconds not in [4, 6, 8]:
            duration_seconds = 8

        if resolution == "1080p" and duration_seconds != 8:
            return {
                "error": "1080p resolution only supports 8-second videos",
                "success": False
            }

        # Generate video using new google-genai SDK
        operation = genai_client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                duration_seconds=duration_seconds,
                negative_prompt=negative_prompt if negative_prompt else None,
                number_of_videos=1,
            ),
        )

        print(f"⏳ Video generation started... (this may take 2-6 minutes)")

        # Poll until completion (max 6 minutes per docs)
        max_wait = 360  # 6 minutes
        waited = 0
        while not operation.done and waited < max_wait:
            time.sleep(10)
            waited += 10
            operation = genai_client.operations.get(operation)
            if waited % 30 == 0:
                print(f"   ... {waited}s elapsed")

        if not operation.done:
            return {
                "error": "Video generation timed out after 6 minutes",
                "success": False
            }

        # Get generated video
        generated_video = operation.response.generated_videos[0]

        # Save video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"veo_{timestamp}.mp4"
        filepath = OUTPUT_DIR / filename

        # Download and save video
        genai_client.files.download(file=generated_video.video)
        generated_video.video.save(str(filepath))

        # Calculate cost based on duration (Veo 3.1: $0.75/second)
        cost = 0.75 * duration_seconds

        return {
            "success": True,
            "video_path": str(filepath.absolute()),
            "filename": filename,
            "model": "veo-3.1-generate-preview",
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "fps": 24,  # Veo 3 generates at 24fps
            "has_audio": True,  # Veo 3.1 natively generates audio
            "estimated_cost_usd": round(cost, 2),
            "timestamp": timestamp,
            "note": "Video includes SynthID watermarking and native audio generation"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": "veo-3.1-generate-preview"
        }


@mcp.tool()
def generate_marketing_content(
    content_type: str,
    topic: str,
    tone: str = "professional",
    length: str = "medium",
    model: str = "claude",
    include_hashtags: bool = True,
) -> Dict[str, Any]:
    """
    Generate marketing content using Claude or Gemini.

    Args:
        content_type: Type of content (social_post, blog_intro, ad_copy, email_subject, product_desc)
        topic: Content topic or product description
        tone: Content tone (professional, casual, enthusiastic, formal)
        length: Content length (short, medium, long)
        model: AI model to use (claude, gemini)
        include_hashtags: Include relevant hashtags (for social content)

    Returns:
        Dictionary with generated content, metadata, and estimated cost
    """
    try:
        length_map = {
            "short": "1-2 sentences",
            "medium": "3-5 sentences or 1 paragraph",
            "long": "2-3 paragraphs"
        }

        prompt_base = f"""Generate {content_type.replace('_', ' ')} about: {topic}

Tone: {tone}
Length: {length_map.get(length, 'medium')}
{'Include relevant hashtags at the end.' if include_hashtags else ''}

Make it compelling, engaging, and ready to use for marketing purposes."""

        content = ""
        tokens_used = 0
        model_used = ""

        if model == "claude" and anthropic_client:
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt_base}
                ]
            )
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            model_used = "claude-sonnet-4"
            cost = (tokens_used / 1000) * PRICING["claude_sonnet"]

        elif model == "gemini" or not anthropic_client:
            # Using Gemini 2.5 Flash Image
            gemini_model = genai.GenerativeModel("gemini-2.5-flash-image")
            response = gemini_model.generate_content(prompt_base)
            content = response.text
            # Approximate token count
            tokens_used = len(content.split()) * 1.3
            model_used = "gemini-2.5-flash-image"
            cost = (tokens_used / 1000) * PRICING["gemini_flash"]

        else:
            return {
                "success": False,
                "error": "No AI model available. Check API keys."
            }

        return {
            "success": True,
            "content": content,
            "content_type": content_type,
            "topic": topic,
            "tone": tone,
            "length": length,
            "model_used": model_used,
            "tokens_used": int(tokens_used),
            "estimated_cost_usd": round(cost, 6),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model
        }


@mcp.tool()
def enhance_prompt_for_photorealism(
    basic_prompt: str,
    subject_type: str = "auto"
) -> Dict[str, Any]:
    """
    Transform a basic prompt into a highly detailed photorealistic prompt for Imagen 4.0.

    This tool helps achieve cinema-quality, photographic realism by adding:
    - Professional photography terminology
    - Lighting and camera specifications
    - Material and texture details
    - Composition and framing guidance

    Args:
        basic_prompt: Simple description (e.g., "bear in a pool with sunglasses")
        subject_type: Type of subject - "animal", "person", "product", "landscape", or "auto"

    Returns:
        Dictionary with enhanced prompts for maximum photorealism

    Example:
        Input: "bear in pool with sunglasses"
        Output: Detailed prompt with lighting, camera settings, material specs, etc.
    """
    try:
        # Photorealism enhancement templates
        photography_terms = [
            "shot on RED Komodo 6K",
            "85mm f/1.4 lens",
            "natural golden hour lighting",
            "shallow depth of field",
            "professional color grading",
            "cinema-quality cinematography",
            "hyperrealistic details",
            "8K resolution quality"
        ]

        lighting_terms = [
            "soft natural sunlight",
            "realistic shadows and highlights",
            "accurate light diffusion",
            "physically accurate lighting",
            "natural ambient occlusion"
        ]

        material_terms = [
            "realistic fur/skin textures",
            "accurate material reflections",
            "natural subsurface scattering",
            "photographic surface details",
            "authentic weathering and imperfections"
        ]

        composition_terms = [
            "professional composition",
            "balanced framing",
            "natural perspective",
            "realistic proportions",
            "authentic environmental integration"
        ]

        # Build enhanced prompt
        enhanced_parts = [
            f"Ultra-photorealistic, cinema-quality photograph: {basic_prompt}.",
            "Shot on RED Komodo 6K with 85mm f/1.4 prime lens.",
            "Natural golden hour lighting with soft shadows and realistic highlights.",
            "Hyperrealistic details: accurate fur/skin textures, material reflections, natural imperfections.",
            "Professional color grading, shallow depth of field, 8K quality.",
            "Authentic environmental integration with physically accurate lighting and shadows.",
            "No CGI look, no cartoon elements, no artificial smoothing.",
            "Pure photographic realism as if captured by a professional wildlife/commercial photographer."
        ]

        enhanced_prompt = " ".join(enhanced_parts)

        # Alternative versions with different emphasis
        alternative_1 = (
            f"Professional editorial photograph: {basic_prompt}. "
            "National Geographic quality, shot on medium format camera (Hasselblad H6D-100c), "
            "natural lighting, hyperrealistic textures, authentic environmental details, "
            "photojournalistic authenticity, zero artificial enhancement, pure documentary realism."
        )

        alternative_2 = (
            f"Commercial photography masterpiece: {basic_prompt}. "
            "Shot on Phase One IQ4 150MP, Schneider Kreuznach 110mm f/2.8 lens, "
            "studio-quality natural light setup, professional retouching (minimal), "
            "billboard-ready resolution, advertising campaign grade, "
            "authentic product photography realism with no fantasy elements."
        )

        return {
            "success": True,
            "original_prompt": basic_prompt,
            "enhanced_prompt": enhanced_prompt,
            "alternatives": {
                "editorial_style": alternative_1,
                "commercial_style": alternative_2
            },
            "tips": [
                "Use 'enhanced_prompt' for maximum photorealism",
                "Avoid words like 'illustration', 'painting', 'artistic', 'fantasy'",
                "Include specific camera models and lens specs for realism",
                "Mention natural lighting and authentic textures",
                "Add 'no CGI look, no cartoon elements' to prevent AI artifacts",
                "Reference professional photography styles (editorial, commercial, documentary)"
            ],
            "negative_prompt_suggestions": [
                "cartoon, illustration, painting, drawing, anime",
                "CGI, 3D render, artificial, synthetic",
                "oversaturated, overprocessed, filters",
                "unrealistic, fantasy, stylized",
                "low quality, blurry, pixelated"
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def generate_social_media_image(
    platform: str,
    description: str,
    primary_text: Optional[str] = None,
    style: str = "photorealistic",
    include_base64: bool = True,
    model_version: str = "imagen-4.0"
) -> Dict[str, Any]:
    """
    Generate platform-optimized social media images ready for direct upload.

    NO URL NEEDED - Returns base64 data for direct platform upload!
    Perfect for Instagram, Facebook, Twitter, LinkedIn, Pinterest, etc.

    Platform Presets (automatically sets correct dimensions):
    - "instagram_feed" → 1:1 square (1024x1024)
    - "instagram_story" → 9:16 vertical (768x1280)
    - "facebook_post" → 16:9 landscape (1280x768)
    - "twitter_post" → 16:9 landscape (1280x768)
    - "linkedin_post" → 16:9 landscape (1280x768)
    - "pinterest_pin" → 3:4 vertical (768x1024)
    - "youtube_thumbnail" → 16:9 landscape (1280x768)
    - "website_hero" → 16:9 landscape (1280x768)
    - "email_header" → 16:9 landscape (1280x768)

    Args:
        platform: Platform preset (e.g., "instagram_feed", "twitter_post")
        description: Scene description for image generation
        primary_text: Optional text to mention in prompt (compositional guidance)
        style: Image style - "photorealistic", "modern_minimal", "bold_vibrant", "elegant"
        include_base64: Include base64 encoding for direct upload (default: True)
        model_version: "imagen-3.0" or "imagen-4.0" (default: "imagen-4.0")

    Returns:
        Dictionary with local_path, base64_data (if enabled), dimensions, and metadata

    Example:
        result = generate_social_media_image(
            platform="instagram_feed",
            description="bear in pool with sunglasses and Coke",
            primary_text="Summer Vibes",
            style="photorealistic"
        )
        # Upload to Instagram API using result["base64_data"]
    """
    try:
        # Platform specifications from Airtable (Synapse Testing base)
        # Source: apprJV9UhYEDNL6J7/tblofKJLzBEcm3Ijr
        PLATFORM_SPECS = {
            # Instagram (1:1 primary, max 2200 chars, 30 hashtags, 30MB, 10 image carousel)
            "instagram_feed": {
                "aspect_ratio": "1:1",
                "note": "Instagram square feed post",
                "max_chars": 2200,
                "max_hashtags": 30,
                "max_size_mb": 30,
                "caption_style": "Short, engaging with emojis; hashtags at end"
            },
            "instagram_story": {
                "aspect_ratio": "9:16",
                "note": "Instagram story (15s video max)",
                "max_chars": 2200,
                "max_size_mb": 30
            },
            "instagram_reel": {
                "aspect_ratio": "9:16",
                "note": "Instagram Reels cover (60s video max)",
                "max_chars": 2200,
                "max_size_mb": 30
            },

            # Facebook (4:5 or 1:1 images, 16:9 videos, max 63206 chars, 10 hashtags, 4GB)
            "facebook_post": {
                "aspect_ratio": "4:5",  # Primary for images
                "alt_aspect_ratio": "1:1",
                "note": "Facebook feed post (images 4:5 or 1:1)",
                "max_chars": 63206,
                "max_hashtags": 10,
                "max_size_gb": 4,
                "caption_style": "Casual and engaging; hashtags at end"
            },
            "facebook_story": {
                "aspect_ratio": "9:16",
                "note": "Facebook story",
                "max_chars": 63206,
                "max_size_gb": 4
            },

            # Twitter/X (1:1 or 16:9, 280 chars STRICT, 2 hashtags, 4 images max, 5MB)
            "twitter_post": {
                "aspect_ratio": "16:9",
                "alt_aspect_ratio": "1:1",
                "note": "Twitter/X feed post (max 4 images, 2m20s video)",
                "max_chars": 280,  # STRICT LIMIT
                "max_hashtags": 2,
                "max_size_mb": 5,
                "max_images": 4,
                "caption_style": "Concise with inline hashtags; brevity critical"
            },

            # LinkedIn (1:1 or 16:9, max 3000 chars, 5 hashtags, 100MB)
            "linkedin_post": {
                "aspect_ratio": "1:1",
                "alt_aspect_ratio": "16:9",
                "note": "LinkedIn feed post (10 min video max)",
                "max_chars": 3000,
                "max_hashtags": 5,
                "max_size_mb": 100,
                "caption_style": "Professional and detailed; hashtags end or inline"
            },

            # YouTube (16:9, 240 min videos, 128GB)
            "youtube_thumbnail": {
                "aspect_ratio": "16:9",
                "note": "YouTube video thumbnail",
                "max_size_gb": 128,
                "caption_style": "Short, engaging descriptions with links"
            },

            # TikTok (9:16 vertical, max 150 chars, 3 hashtags, 287MB, 10 min videos)
            "tiktok_cover": {
                "aspect_ratio": "9:16",
                "note": "TikTok video cover (10 min video max)",
                "max_chars": 150,
                "max_hashtags": 3,
                "max_size_mb": 287,
                "caption_style": "Minimal captions; focus on video content"
            },

            # Pinterest (3:4 vertical for pins)
            "pinterest_pin": {
                "aspect_ratio": "3:4",
                "note": "Pinterest standard pin (2:3 preferred)",
            },

            # Generic web/email formats
            "website_hero": {
                "aspect_ratio": "16:9",
                "note": "Website hero section"
            },
            "blog_featured": {
                "aspect_ratio": "16:9",
                "note": "Blog featured image"
            },
            "email_header": {
                "aspect_ratio": "16:9",
                "note": "Email header image"
            },
        }

        if platform not in PLATFORM_SPECS:
            return {
                "success": False,
                "error": f"Unknown platform: {platform}",
                "supported_platforms": list(PLATFORM_SPECS.keys())
            }

        spec = PLATFORM_SPECS[platform]
        aspect_ratio = spec["aspect_ratio"]

        # Build enhanced prompt based on style
        style_prompts = {
            "photorealistic": (
                "Ultra-photorealistic, professional photography. "
                "Shot on high-end camera with natural lighting. "
                "Hyperrealistic details, authentic textures. "
                "No CGI, no cartoon elements."
            ),
            "modern_minimal": (
                "Clean, modern, minimalist aesthetic. "
                "Simple composition, ample negative space. "
                "Contemporary design, professional quality."
            ),
            "bold_vibrant": (
                "Bold, vibrant, eye-catching colors. "
                "High contrast, energetic composition. "
                "Dynamic, attention-grabbing visual."
            ),
            "elegant": (
                "Elegant, sophisticated, luxurious aesthetic. "
                "Refined composition, premium quality. "
                "High-end editorial style."
            )
        }

        style_addition = style_prompts.get(style, style_prompts["photorealistic"])

        # Build full prompt
        full_prompt = f"{description}. {style_addition}"

        if primary_text:
            full_prompt += f" Compositionally designed for text overlay: '{primary_text}'."

        # Add platform-specific guidance
        if "story" in platform or "reel" in platform or "tiktok" in platform:
            full_prompt += " Vertical format optimized for mobile viewing, subject centered."
        elif "pinterest" in platform:
            full_prompt += " Vertical format optimized for Pinterest browsing."
        elif "instagram_feed" in platform:
            full_prompt += " Square format, balanced composition, mobile-optimized."
        else:
            full_prompt += " Horizontal format, professional composition."

        logger.info(f"Generating {platform} image: {full_prompt[:100]}...")

        # Generate image using Imagen
        model_id = f"{model_version}-generate-001" if "4" in model_version else "imagen-3.0-generate-001"

        response = genai_client.models.generate_images(
            model=model_id,
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                image_size="1K",
                aspect_ratio=aspect_ratio,
                person_generation="allow_adult",
            ),
        )

        # Save locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{timestamp}.png"
        filepath = OUTPUT_DIR / filename

        response.generated_images[0].image.save(str(filepath))

        logger.info(f"Image saved: {filepath}")

        # Get file size
        file_size_mb = filepath.stat().st_size / (1024 * 1024)

        # Calculate cost
        cost = PRICING.get(f"imagen4_1k" if "4" in model_version else "imagen3_1k", 0.04)

        result = {
            "success": True,
            "platform": platform,
            "platform_note": spec["note"],
            "aspect_ratio": aspect_ratio,
            "local_path": str(filepath),
            "filename": filename,
            "file_size_mb": round(file_size_mb, 2),
            "estimated_cost_usd": cost,
            "model": model_version,
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "usage_note": "Image ready for direct upload to platform API - no URL needed!",
            # Platform-specific limits from Airtable
            "platform_limits": {
                "max_chars": spec.get("max_chars"),
                "max_hashtags": spec.get("max_hashtags"),
                "max_size_mb": spec.get("max_size_mb"),
                "max_size_gb": spec.get("max_size_gb"),
                "max_images": spec.get("max_images"),
                "caption_style": spec.get("caption_style"),
                "alt_aspect_ratio": spec.get("alt_aspect_ratio")
            }
        }

        # Add base64 encoding if requested (for direct platform upload)
        if include_base64:
            with open(filepath, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                result["base64_data"] = f"data:image/png;base64,{encoded}"
                result["base64_size_kb"] = round(len(encoded) / 1024, 2)

        return result

    except Exception as e:
        logger.error(f"Social media image generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "platform": platform
        }


@mcp.tool()
def batch_generate_social_set(
    description: str,
    platforms: List[str],
    primary_text: Optional[str] = None,
    style: str = "photorealistic",
    include_base64: bool = True,
    model_version: str = "imagen-4.0"
) -> Dict[str, Any]:
    """
    Generate a complete social media campaign across multiple platforms in one call.

    Perfect for launching coordinated campaigns with platform-optimized images
    for Instagram, Facebook, Twitter, LinkedIn, Pinterest, etc.

    Args:
        description: Scene description for all images
        platforms: List of platforms (e.g., ["instagram_feed", "twitter_post", "linkedin_post"])
        primary_text: Optional text for all images
        style: Image style for all platforms
        include_base64: Include base64 encoding for all images (default: True)
        model_version: "imagen-3.0" or "imagen-4.0" (default: "imagen-4.0")

    Returns:
        Dictionary with results for each platform, total cost, and summary

    Example:
        # Generate complete campaign
        result = batch_generate_social_set(
            description="bear in pool with sunglasses and Coke",
            platforms=["instagram_feed", "twitter_post", "pinterest_pin"],
            primary_text="Summer Vibes",
            style="photorealistic"
        )

        # Access individual platform results
        instagram_data = result["results"]["instagram_feed"]
        twitter_data = result["results"]["twitter_post"]

        # Upload to each platform
        instagram_api.create_post(image_data=instagram_data["base64_data"])
        twitter_api.create_post(image_data=twitter_data["base64_data"])
    """
    try:
        logger.info(f"Starting batch generation for {len(platforms)} platforms")

        results = {}
        successful = 0
        failed = 0
        total_cost = 0.0
        failed_platforms = []

        # Generate for each platform
        for i, platform in enumerate(platforms, 1):
            logger.info(f"Generating {i}/{len(platforms)}: {platform}")

            result = generate_social_media_image(
                platform=platform,
                description=description,
                primary_text=primary_text,
                style=style,
                include_base64=include_base64,
                model_version=model_version
            )

            results[platform] = result

            if result.get("success"):
                successful += 1
                total_cost += result.get("estimated_cost_usd", 0)
            else:
                failed += 1
                failed_platforms.append(platform)

        # Build summary
        summary = {
            "success": True,
            "total_platforms": len(platforms),
            "successful": successful,
            "failed": failed,
            "failed_platforms": failed_platforms,
            "results": results,
            "total_cost_usd": round(total_cost, 4),
            "model": model_version,
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "campaign_description": description
        }

        # Add file paths summary
        if successful > 0:
            summary["generated_files"] = [
                {
                    "platform": platform,
                    "file": result.get("filename"),
                    "path": result.get("local_path"),
                    "has_base64": "base64_data" in result
                }
                for platform, result in results.items()
                if result.get("success")
            ]

        logger.info(f"Batch generation complete: {successful}/{len(platforms)} successful")

        return summary

    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "platforms": platforms
        }


@mcp.tool()
def calculate_cost_estimate(
    images_1k: int = 0,
    images_2k: int = 0,
    video_seconds: int = 0,
    content_pieces: int = 0,
    image_model: str = "imagen-3.0",
    video_model: str = "veo3",
) -> Dict[str, Any]:
    """
    Calculate estimated costs for a marketing campaign.

    Args:
        images_1k: Number of 1K resolution images
        images_2k: Number of 2K resolution images
        video_seconds: Total seconds of video
        content_pieces: Number of content pieces (avg 500 tokens each)
        image_model: Image model - "imagen-3.0" or "imagen-4.0"
        video_model: Video model - "veo2", "veo3", or "veo3_fast"

    Returns:
        Dictionary with detailed cost breakdown
    """
    try:
        # Image costs
        if "4.0" in image_model or "4" in image_model:
            cost_1k = PRICING["imagen4_1k"]
            cost_2k = PRICING["imagen4_2k"]
            model_name = "imagen-4.0"
        else:
            cost_1k = PRICING["imagen3_1k"]
            cost_2k = PRICING["imagen3_2k"]
            model_name = "imagen-3.0"

        image_1k_cost = images_1k * cost_1k
        image_2k_cost = images_2k * cost_2k
        total_image_cost = image_1k_cost + image_2k_cost

        # Video costs
        video_model_key = video_model.lower()
        if video_model_key not in PRICING:
            video_model_key = "veo3"

        video_cost = video_seconds * PRICING[video_model_key]

        # Content generation costs (assuming avg 500 tokens per piece with Gemini)
        content_cost = content_pieces * (0.5 * PRICING["gemini_flash"])

        # Total
        total_cost = total_image_cost + video_cost + content_cost

        return {
            "success": True,
            "breakdown": {
                "images": {
                    "1k_resolution": {
                        "count": images_1k,
                        "cost_per_image": cost_1k,
                        "cost_usd": round(image_1k_cost, 4)
                    },
                    "2k_resolution": {
                        "count": images_2k,
                        "cost_per_image": cost_2k,
                        "cost_usd": round(image_2k_cost, 4)
                    },
                    "total_cost_usd": round(total_image_cost, 4),
                    "model": model_name
                },
                "video": {
                    "seconds": video_seconds,
                    "model": video_model_key,
                    "cost_per_second": PRICING[video_model_key],
                    "cost_usd": round(video_cost, 4)
                },
                "content": {
                    "pieces": content_pieces,
                    "avg_tokens": 500,
                    "model": "gemini-2.5-flash-image",
                    "cost_usd": round(content_cost, 6)
                }
            },
            "total_cost_usd": round(total_cost, 4),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.resource("config://pricing")
def get_pricing_info() -> str:
    """Get current pricing information for all services."""
    return json.dumps({
        "pricing": PRICING,
        "currency": "USD",
        "last_updated": "2025-11-09",
        "notes": "Official pricing from Gemini API documentation",
        "details": {
            "imagen": "Per image pricing - 1K or 2K resolution",
            "veo": "Per second of video - 24fps with audio",
            "content": "Per 1K tokens"
        }
    }, indent=2)


@mcp.resource("config://models")
def get_available_models() -> str:
    """Get information about available AI models."""
    return json.dumps({
        "image_generation": {
            "imagen-3.0": {
                "api_model": "imagen-3.0-generate-002",
                "resolutions": ["1K", "2K"],
                "aspect_ratios": ["1:1", "3:4", "4:3", "9:16", "16:9"],
                "max_images": 4,
                "max_prompt_tokens": 480,
                "features": ["SynthID watermarking", "text in images", "photorealism"]
            },
            "imagen-4.0": {
                "api_model": "imagen-4.0-generate-001",
                "resolutions": ["1K", "2K"],
                "aspect_ratios": ["1:1", "3:4", "4:3", "9:16", "16:9"],
                "max_images": 4,
                "max_prompt_tokens": 480,
                "features": ["Ultra quality", "SynthID watermarking", "advanced prompting"],
                "variants": ["standard", "ultra", "fast"]
            }
        },
        "video_generation": {
            "veo-3.0": {
                "api_model": "veo-3.0-generate-001",
                "durations": [4, 6, 8],
                "resolutions": ["720p", "1080p"],
                "aspect_ratios": ["16:9", "9:16"],
                "fps": 24,
                "features": ["Native audio generation", "SynthID watermarking", "reference images"]
            },
            "veo-3.1-preview": {
                "api_model": "veo-3.1-generate-preview",
                "durations": [4, 6, 8],
                "resolutions": ["720p", "1080p"],
                "aspect_ratios": ["16:9", "9:16"],
                "fps": 24,
                "features": ["Video extension (7+ seconds)", "Frame-specific generation", "Up to 3 reference images"]
            }
        },
        "content_generation": {
            "claude-sonnet-4": {
                "model": "claude-sonnet-4-20250514",
                "strengths": ["creative writing", "nuanced tone", "long-form content"]
            },
            "gemini-2.5-flash-image": {
                "model": "gemini-2.5-flash-image",
                "strengths": ["multimodal understanding", "fast generation", "cost-effective", "image context"]
            }
        }
    }, indent=2)


@mcp.prompt()
def campaign_planner():
    """Generate a comprehensive marketing campaign plan."""
    return """You are a marketing campaign strategist. Help plan a comprehensive marketing campaign.

Please provide:
1. Campaign objective and target audience
2. Key messages and value propositions
3. Content mix (images, videos, copy)
4. Channel strategy (social, email, ads)
5. Timeline and milestones

I'll help you:
- Generate cost estimates
- Create visual assets with Imagen
- Produce video content with Veo
- Write compelling copy with Claude/Gemini
- Optimize for different platforms

What campaign would you like to plan?"""


@mcp.prompt()
def image_prompt_enhancer():
    """Enhance image generation prompts for better results."""
    return """I'll help you create better prompts for Imagen image generation.

For best results, include:
- **Subject**: What is the main focus?
- **Style**: Photography, illustration, 3D render, etc.
- **Mood**: Professional, playful, luxurious, etc.
- **Composition**: Layout, framing, perspective
- **Details**: Colors, lighting, background, textures
- **Quality terms**: High detail, sharp focus, professional lighting

Example: "Professional product photography of a smartphone, centered composition,
white background, soft studio lighting, high detail, commercial quality, modern and clean aesthetic"

What image do you want to create?"""


if __name__ == "__main__":
    # Run server in HTTP mode for deployment
    # For local testing with Claude Desktop, use: mcp.run() for STDIO
    import sys

    transport = "stdio"  # Default for Claude Desktop

    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        transport = "http"

    mcp.run(transport=transport)
