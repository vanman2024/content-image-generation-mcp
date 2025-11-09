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
    Generate marketing videos using Google Veo 3 via Gemini API.

    ⚠️ COST WARNING: Video generation is expensive!
    - 4 seconds = $3.00
    - 6 seconds = $4.50
    - 8 seconds = $6.00

    Consider using Veo Fast models for 50% cost reduction.

    Args:
        prompt: Detailed description of the video to generate (supports audio cues)
        duration_seconds: Video duration - 4, 6, or 8 seconds (default: 8)
        resolution: Video resolution - "720p" or "1080p" (1080p limited to 8s)
        aspect_ratio: Video aspect ratio - "16:9" or "9:16" (default: "16:9")
        negative_prompt: Elements to exclude from the video

    Returns:
        Dictionary with video path, metadata, and estimated cost
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
