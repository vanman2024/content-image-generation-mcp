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
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP
from dotenv import load_dotenv

# Anthropic Claude
from anthropic import Anthropic

# Google Generative AI (Gemini API)
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(name=os.getenv("MCP_SERVER_NAME", "Content & Image Generation"))

# Configuration
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Anthropic
anthropic_client = None
if os.getenv("ANTHROPIC_API_KEY"):
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize Gemini API
if os.getenv("GOOGLE_API_KEY"):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
else:
    raise ValueError("GOOGLE_API_KEY environment variable is required")


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
def generate_image_imagen3(
    prompt: str,
    negative_prompt: Optional[str] = None,
    aspect_ratio: str = "1:1",
    number_of_images: int = 1,
    image_size: str = "1K",
    output_format: str = "png",
    model_version: str = "imagen-3.0",
) -> Dict[str, Any]:
    """
    Generate marketing images using Google Imagen 3/4 via Gemini API.

    Args:
        prompt: Detailed description of the image to generate (max 480 tokens)
        negative_prompt: What to avoid in the image
        aspect_ratio: Image aspect ratio - "1:1", "3:4", "4:3", "9:16", "16:9"
        number_of_images: Number of images to generate (1-4)
        image_size: Image size - "1K" or "2K" (2K only for Standard/Ultra models)
        output_format: Output format (png, jpeg, webp)
        model_version: Model to use - "imagen-3.0" or "imagen-4.0"

    Returns:
        Dictionary with image paths, metadata, and estimated cost
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            return {
                "error": "GOOGLE_API_KEY not configured",
                "success": False
            }

        # Validate parameters
        if number_of_images < 1 or number_of_images > 4:
            number_of_images = 1

        # Map model version to Gemini API model ID
        model_map = {
            "imagen-3.0": "imagen-3.0-generate-002",
            "imagen-4.0": "imagen-4.0-generate-001",
            "imagen-4.0-ultra": "imagen-4.0-ultra-generate-001",
            "imagen-4.0-fast": "imagen-4.0-fast-generate-001"
        }

        model_id = model_map.get(model_version, "imagen-3.0-generate-002")

        # Initialize Gemini model for image generation
        model = genai.GenerativeModel(model_id)

        # Generate images using Gemini API
        config = {
            "number_of_images": number_of_images,
            "aspect_ratio": aspect_ratio,
        }

        # Only Standard/Ultra models support 2K
        if image_size == "2K" and "fast" not in model_id.lower():
            config["image_size"] = "2K"

        if negative_prompt:
            config["negative_prompt"] = negative_prompt

        # Generate images
        response = model.generate_images(
            prompt=prompt,
            config=config
        )

        # Save all generated images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_images = []

        for i, image in enumerate(response.images):
            filename = f"imagen_{model_version}_{timestamp}_{i+1}.{output_format}"
            filepath = OUTPUT_DIR / filename

            # Decode base64 and save
            import base64
            image_bytes = base64.b64decode(image.data)

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            saved_images.append({
                "image_path": str(filepath.absolute()),
                "filename": filename
            })

        # Calculate cost based on model and size
        if "4.0" in model_version:
            cost_per_image = 0.04 if image_size == "1K" else 0.08
        else:  # Imagen 3.0
            cost_per_image = 0.02 if image_size == "1K" else 0.04

        total_cost = cost_per_image * number_of_images

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
        return {
            "success": False,
            "error": str(e),
            "model": model_version
        }


@mcp.tool()
def batch_generate_images(
    prompts: List[str],
    aspect_ratio: str = "1:1",
    quality: str = "hd",
    model_version: str = "imagen3",
) -> Dict[str, Any]:
    """
    Generate multiple marketing images in batch.

    Args:
        prompts: List of image prompts
        aspect_ratio: Image aspect ratio for all images
        quality: Image quality (sd or hd)
        model_version: Model to use (imagen3 or imagen4)

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
            quality=quality
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
        if not os.getenv("GOOGLE_API_KEY"):
            return {
                "error": "GOOGLE_API_KEY not configured",
                "success": False
            }

        # Validate parameters
        if duration_seconds not in [4, 6, 8]:
            duration_seconds = 8

        if resolution == "1080p" and duration_seconds != 8:
            return {
                "error": "1080p resolution only supports 8-second videos",
                "success": False
            }

        # Initialize Gemini client for video generation
        import time

        # Generate video using Gemini API's long-running operation pattern
        # Model: veo-3.0-generate-001 (stable) or veo-3.1-generate-preview
        model = genai.GenerativeModel("veo-3.0-generate-001")

        # Start video generation operation
        config = {
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration_seconds": str(duration_seconds)
        }

        if negative_prompt:
            config["negative_prompt"] = negative_prompt

        # Note: Gemini API uses generate_videos() which returns a long-running operation
        # This is a synchronous wrapper - in production, use async polling
        operation = genai.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=prompt,
            config=config
        )

        # Poll until completion (max 6 minutes per docs)
        max_wait = 360  # 6 minutes
        waited = 0
        while not operation.done and waited < max_wait:
            time.sleep(10)
            waited += 10
            operation = genai.operations.get(operation.name)

        if not operation.done:
            return {
                "error": "Video generation timed out after 6 minutes",
                "success": False
            }

        # Extract video from operation response
        video_data = operation.response.generated_videos[0].video

        # Save video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"veo3_{timestamp}.mp4"
        filepath = OUTPUT_DIR / filename

        # Write video bytes to file
        with open(filepath, 'wb') as f:
            f.write(video_data)

        # Calculate cost based on duration (Veo 3: $0.75/second)
        cost = 0.75 * duration_seconds

        return {
            "success": True,
            "video_path": str(filepath.absolute()),
            "filename": filename,
            "model": "veo-3.0-generate-001",
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "fps": 24,  # Veo 3 generates at 24fps
            "has_audio": True,  # Veo 3.0 and 3.1 natively generate audio
            "estimated_cost_usd": round(cost, 2),
            "timestamp": timestamp,
            "note": "Video includes SynthID watermarking and audio generation"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": "veo-3.0-generate-001"
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
