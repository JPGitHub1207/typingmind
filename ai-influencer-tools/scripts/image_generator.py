"""
AI Influencer Image Generator
Generate consistent character images using various AI image generation services.

Usage:
    python image_generator.py --prompt "beach sunset" --style casual --count 4
    python image_generator.py --template lifestyle --environment cafe
"""

import os
import json
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

# You'll need to install APIs you plan to use:
# pip install openai stability-sdk replicate

# Load character configuration
CONFIG_PATH = Path(__file__).parent.parent / "config" / "character_config.json"

def load_character_config() -> dict:
    """Load character configuration from JSON file."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

CHARACTER = load_character_config()


@dataclass
class ImageRequest:
    prompt: str
    negative_prompt: str
    width: int = 1024
    height: int = 1024
    style: str = "casual"
    count: int = 1
    seed: Optional[int] = None


# Prompt building blocks
OUTFIT_OPTIONS = {
    "casual": "wearing oversized cream sweater and high-waisted jeans, white sneakers",
    "streetwear": "wearing black oversized hoodie, cargo pants, chunky platform boots",
    "elegant": "wearing tailored blazer, silk blouse, fitted trousers, heels",
    "athletic": "wearing matching workout set, running shoes, hair in ponytail",
    "summer": "wearing flowy sundress, sandals, minimal jewelry",
    "evening": "wearing sleek slip dress, statement earrings, strappy heels",
    "cozy": "wearing knit cardigan, leggings, fuzzy socks, holding mug",
}

POSE_OPTIONS = {
    "standing": "standing naturally, relaxed pose",
    "sitting": "sitting elegantly, legs crossed",
    "walking": "walking confidently, candid movement",
    "looking_away": "looking to the side thoughtfully, profile view",
    "laughing": "genuine laugh, joyful expression, eyes crinkled",
    "working": "focused on laptop/phone, natural concentration",
    "selfie": "taking selfie, slight smile, phone visible",
}

ENVIRONMENT_OPTIONS = {
    "cafe": "in a minimalist coffee shop, warm lighting, plants visible",
    "street": "on a city street, urban background, golden hour light",
    "home": "in a modern apartment, clean aesthetic, natural light from window",
    "rooftop": "on a rooftop at sunset, city skyline in background",
    "nature": "in a botanical garden, lush greenery, soft natural light",
    "studio": "in a photography studio, clean white background, professional lighting",
    "beach": "on a beach at golden hour, ocean in background, warm tones",
    "gallery": "in an art gallery, minimalist white walls, interesting artwork visible",
}

LIGHTING_OPTIONS = {
    "golden_hour": "golden hour lighting, warm tones, soft shadows",
    "natural": "soft natural lighting, diffused daylight",
    "studio": "professional studio lighting, clean and even",
    "neon": "neon lighting accents, cyberpunk atmosphere, colorful glow",
    "dramatic": "dramatic side lighting, cinematic shadows",
    "overcast": "soft overcast lighting, no harsh shadows, even tones",
}

STYLE_MODIFIERS = {
    "editorial": "fashion photography, vogue style, professional quality",
    "candid": "candid lifestyle photography, authentic moment",
    "artistic": "creative composition, artistic perspective, unique angle",
    "cinematic": "cinematic photography, film grain, dramatic mood",
    "minimal": "minimalist composition, clean aesthetic, lots of negative space",
}


def build_prompt(
    outfit: str = "casual",
    pose: str = "standing",
    environment: str = "street",
    lighting: str = "golden_hour",
    style: str = "candid",
    custom_details: str = ""
) -> str:
    """Build a complete prompt from components."""
    
    char_config = CHARACTER.get("visual_identity", {}).get("appearance", {})
    prompt_config = CHARACTER.get("prompt_templates", {})
    
    # Character base description
    char_name = CHARACTER.get("character", {}).get("name", "Nova")
    char_base = f"{char_name}, 24 year old AI influencer"
    
    # Appearance details
    hair = char_config.get("hair", "silver lavender bob hair")
    eyes = char_config.get("eyes", "violet eyes with subtle digital reflection")
    
    # Build the prompt
    components = [
        char_base,
        hair,
        eyes,
        OUTFIT_OPTIONS.get(outfit, outfit),
        POSE_OPTIONS.get(pose, pose),
        ENVIRONMENT_OPTIONS.get(environment, environment),
        LIGHTING_OPTIONS.get(lighting, lighting),
        STYLE_MODIFIERS.get(style, style),
        "hyperrealistic photography, 8k, highly detailed, beautiful composition"
    ]
    
    if custom_details:
        components.insert(-1, custom_details)
    
    return ", ".join(components)


def get_negative_prompt() -> str:
    """Get the standard negative prompt."""
    prompt_config = CHARACTER.get("prompt_templates", {})
    default_negative = (
        "deformed, bad anatomy, disfigured, poorly drawn face, mutation, "
        "mutated, extra limb, ugly, poorly drawn hands, missing limb, "
        "floating limbs, disconnected limbs, malformed hands, blurry, "
        "watermark, oversaturated, distorted face, bad proportions, "
        "duplicate, low quality, text, logo, worst quality, jpeg artifacts"
    )
    return prompt_config.get("base_negative", default_negative)


def generate_with_stability(request: ImageRequest, api_key: str) -> List[bytes]:
    """Generate images using Stability AI API."""
    try:
        from stability_sdk import client
        import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
        
        stability_api = client.StabilityInference(
            key=api_key,
            engine="stable-diffusion-xl-1024-v1-0"
        )
        
        answers = stability_api.generate(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            samples=request.count,
            seed=request.seed or 0
        )
        
        images = []
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.type == generation.ARTIFACT_IMAGE:
                    images.append(artifact.binary)
        
        return images
        
    except ImportError:
        print("❌ stability-sdk not installed. Run: pip install stability-sdk")
        return []
    except Exception as e:
        print(f"❌ Stability AI error: {e}")
        return []


def generate_with_openai(request: ImageRequest, api_key: str) -> List[str]:
    """Generate images using OpenAI DALL-E 3."""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        images = []
        for i in range(request.count):
            response = client.images.generate(
                model="dall-e-3",
                prompt=request.prompt,
                size=f"{request.width}x{request.height}",
                quality="hd",
                n=1
            )
            images.append(response.data[0].url)
        
        return images
        
    except ImportError:
        print("❌ openai not installed. Run: pip install openai")
        return []
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return []


def generate_with_replicate(request: ImageRequest, api_token: str) -> List[str]:
    """Generate images using Replicate (various models)."""
    try:
        import replicate
        
        # Use SDXL model
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "width": request.width,
                "height": request.height,
                "num_outputs": request.count,
                "seed": request.seed
            }
        )
        
        return list(output)
        
    except ImportError:
        print("❌ replicate not installed. Run: pip install replicate")
        return []
    except Exception as e:
        print(f"❌ Replicate error: {e}")
        return []


def save_images(images: List, output_dir: str = "assets/images/generated") -> List[Path]:
    """Save generated images to disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, img in enumerate(images):
        filename = f"gen_{timestamp}_{i+1}.png"
        filepath = output_path / filename
        
        if isinstance(img, bytes):
            with open(filepath, "wb") as f:
                f.write(img)
        elif isinstance(img, str) and img.startswith("http"):
            # Download from URL
            import requests
            response = requests.get(img)
            with open(filepath, "wb") as f:
                f.write(response.content)
        
        saved_paths.append(filepath)
        print(f"✅ Saved: {filepath}")
    
    return saved_paths


def generate_batch(
    templates: List[Dict],
    provider: str = "replicate",
    output_dir: str = "assets/images/batch"
) -> List[Path]:
    """Generate a batch of images from template definitions."""
    
    all_paths = []
    
    for i, template in enumerate(templates):
        print(f"\n📸 Generating {i+1}/{len(templates)}: {template.get('name', 'Untitled')}")
        
        prompt = build_prompt(
            outfit=template.get("outfit", "casual"),
            pose=template.get("pose", "standing"),
            environment=template.get("environment", "street"),
            lighting=template.get("lighting", "golden_hour"),
            style=template.get("style", "candid"),
            custom_details=template.get("custom", "")
        )
        
        request = ImageRequest(
            prompt=prompt,
            negative_prompt=get_negative_prompt(),
            width=template.get("width", 1024),
            height=template.get("height", 1344),  # 3:4 ratio for Instagram
            count=template.get("count", 1)
        )
        
        # Generate based on provider
        api_key = os.getenv("REPLICATE_API_TOKEN") or os.getenv("STABILITY_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if provider == "replicate" and os.getenv("REPLICATE_API_TOKEN"):
            images = generate_with_replicate(request, os.getenv("REPLICATE_API_TOKEN"))
        elif provider == "stability" and os.getenv("STABILITY_API_KEY"):
            images = generate_with_stability(request, os.getenv("STABILITY_API_KEY"))
        elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
            images = generate_with_openai(request, os.getenv("OPENAI_API_KEY"))
        else:
            print(f"⚠️ No API key found for {provider}")
            images = []
        
        if images:
            paths = save_images(images, output_dir)
            all_paths.extend(paths)
    
    return all_paths


def create_weekly_content_batch() -> List[Dict]:
    """Create a batch definition for a week's worth of content."""
    
    batch = [
        # Monday - Motivational
        {
            "name": "Monday Motivation",
            "outfit": "streetwear",
            "pose": "walking",
            "environment": "street",
            "lighting": "golden_hour",
            "style": "candid",
            "count": 2
        },
        # Tuesday - Tech/Work
        {
            "name": "Tuesday Work Life",
            "outfit": "elegant",
            "pose": "working",
            "environment": "cafe",
            "lighting": "natural",
            "style": "minimal",
            "count": 2
        },
        # Wednesday - Fashion
        {
            "name": "Wednesday Style",
            "outfit": "evening",
            "pose": "standing",
            "environment": "gallery",
            "lighting": "studio",
            "style": "editorial",
            "count": 3
        },
        # Thursday - Lifestyle
        {
            "name": "Thursday Vibes",
            "outfit": "cozy",
            "pose": "sitting",
            "environment": "home",
            "lighting": "natural",
            "style": "candid",
            "count": 2
        },
        # Friday - Fun
        {
            "name": "Friday Energy",
            "outfit": "streetwear",
            "pose": "laughing",
            "environment": "rooftop",
            "lighting": "golden_hour",
            "style": "cinematic",
            "count": 2
        },
        # Saturday - Adventure
        {
            "name": "Saturday Adventure",
            "outfit": "casual",
            "pose": "walking",
            "environment": "nature",
            "lighting": "golden_hour",
            "style": "candid",
            "count": 2
        },
        # Sunday - Reflection
        {
            "name": "Sunday Reflection",
            "outfit": "cozy",
            "pose": "looking_away",
            "environment": "beach",
            "lighting": "golden_hour",
            "style": "artistic",
            "count": 2
        }
    ]
    
    return batch


def main():
    parser = argparse.ArgumentParser(description="AI Influencer Image Generator")
    parser.add_argument("--prompt", "-p", help="Custom prompt (overrides template)")
    parser.add_argument("--outfit", "-o", default="casual",
                       choices=list(OUTFIT_OPTIONS.keys()),
                       help="Outfit style")
    parser.add_argument("--pose", default="standing",
                       choices=list(POSE_OPTIONS.keys()),
                       help="Pose type")
    parser.add_argument("--environment", "-e", default="street",
                       choices=list(ENVIRONMENT_OPTIONS.keys()),
                       help="Environment/location")
    parser.add_argument("--lighting", "-l", default="golden_hour",
                       choices=list(LIGHTING_OPTIONS.keys()),
                       help="Lighting style")
    parser.add_argument("--style", "-s", default="candid",
                       choices=list(STYLE_MODIFIERS.keys()),
                       help="Photography style")
    parser.add_argument("--count", "-c", type=int, default=1,
                       help="Number of images to generate")
    parser.add_argument("--provider", default="replicate",
                       choices=["replicate", "stability", "openai"],
                       help="Image generation provider")
    parser.add_argument("--batch", "-b", action="store_true",
                       help="Generate weekly content batch")
    parser.add_argument("--output", default="assets/images/generated",
                       help="Output directory")
    parser.add_argument("--preview", action="store_true",
                       help="Preview prompt without generating")
    
    args = parser.parse_args()
    
    if args.batch:
        print("📅 Generating weekly content batch...")
        batch = create_weekly_content_batch()
        paths = generate_batch(batch, args.provider, args.output)
        print(f"\n✅ Generated {len(paths)} images for the week")
        
    elif args.prompt:
        # Use custom prompt directly
        request = ImageRequest(
            prompt=args.prompt,
            negative_prompt=get_negative_prompt(),
            count=args.count
        )
        print(f"📸 Using custom prompt: {args.prompt[:100]}...")
        
    else:
        # Build prompt from components
        prompt = build_prompt(
            outfit=args.outfit,
            pose=args.pose,
            environment=args.environment,
            lighting=args.lighting,
            style=args.style
        )
        
        if args.preview:
            print("\n📝 Generated Prompt:")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            print("\n📝 Negative Prompt:")
            print("-" * 50)
            print(get_negative_prompt())
            return
        
        request = ImageRequest(
            prompt=prompt,
            negative_prompt=get_negative_prompt(),
            count=args.count
        )
        
        print(f"\n📸 Generating {args.count} image(s)...")
        print(f"   Outfit: {args.outfit}")
        print(f"   Pose: {args.pose}")
        print(f"   Environment: {args.environment}")
        print(f"   Style: {args.style}")
        
        # Generate based on provider
        if args.provider == "replicate":
            images = generate_with_replicate(request, os.getenv("REPLICATE_API_TOKEN", ""))
        elif args.provider == "stability":
            images = generate_with_stability(request, os.getenv("STABILITY_API_KEY", ""))
        elif args.provider == "openai":
            images = generate_with_openai(request, os.getenv("OPENAI_API_KEY", ""))
        
        if images:
            save_images(images, args.output)
        else:
            print("\n💡 To generate images, set up your API key:")
            print("   export REPLICATE_API_TOKEN=your_token")
            print("   export STABILITY_API_KEY=your_key")
            print("   export OPENAI_API_KEY=your_key")
            print("\n   Or use --preview to see the prompt")


if __name__ == "__main__":
    main()
