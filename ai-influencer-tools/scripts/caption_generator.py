"""
AI Influencer Caption Generator
Uses GPT-4/Claude to generate on-brand captions for social media posts.

Usage:
    python caption_generator.py --image "beach_sunset.png" --type "lifestyle" --platform "instagram"
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# You'll need to install: pip install openai python-dotenv
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# Character configuration - customize this for your AI influencer
CHARACTER_CONFIG = {
    "name": "Nova",
    "personality": "Curious, optimistic, tech-savvy, slightly quirky",
    "tone": "Friendly and approachable, uses modern slang sparingly",
    "emoji_style": "moderate",  # none, minimal, moderate, heavy
    "values": ["authenticity", "creativity", "innovation", "sustainability"],
    "catchphrases": [
        "Living in the future, one pixel at a time ✨",
        "Glitching through life beautifully",
        "Coded with love 💜"
    ],
    "topics_to_avoid": ["politics", "controversy", "negativity"],
    "hashtag_count": 25
}

# Caption templates by content type
CAPTION_TEMPLATES = {
    "lifestyle": """
Create an engaging Instagram caption for a lifestyle photo.

Character: {name}
Personality: {personality}
Tone: {tone}

Photo description: {image_description}
Mood: {mood}

Requirements:
- Start with a hook (question or bold statement) that appears in preview
- 2-3 sentences of personal reflection or story
- End with a soft call-to-action
- Include {hashtag_count} relevant hashtags after a line break
- Use emojis: {emoji_style}

Caption:
""",
    
    "fashion": """
Create a fashion-focused Instagram caption.

Character: {name}
Personality: {personality}  
Tone: {tone}

Outfit/Look description: {image_description}
Setting: {setting}

Requirements:
- Hook that highlights the look or vibe
- Brief styling note or fashion philosophy
- Tag fictional or real brands naturally (use [BRAND] placeholders)
- Call-to-action asking for style opinions
- {hashtag_count} fashion-relevant hashtags
- Emojis: {emoji_style}

Caption:
""",

    "inspirational": """
Create an inspirational Instagram caption.

Character: {name}
Personality: {personality}
Tone: {tone}
Core values: {values}

Image context: {image_description}
Theme: {theme}

Requirements:
- Powerful opening line
- Personal story or observation (2-3 sentences)
- Universal lesson or takeaway
- Question to encourage reflection
- {hashtag_count} motivational hashtags
- Emojis: {emoji_style}

Caption:
""",

    "product": """
Create a sponsored/product integration caption.

Character: {name}
Personality: {personality}
Tone: {tone}

Product: {product_name}
Key features: {product_features}
Image context: {image_description}

Requirements:
- Natural hook (NOT salesy)
- Personal experience with product
- 1-2 specific benefits mentioned casually
- Include #ad or #sponsored naturally
- Soft CTA (not pushy)
- {hashtag_count} relevant hashtags
- Emojis: {emoji_style}

Caption:
""",

    "engagement": """
Create an engagement-focused caption designed to spark conversation.

Character: {name}
Personality: {personality}
Tone: {tone}

Image context: {image_description}
Topic: {topic}

Requirements:
- Relatable statement or hot take
- Brief personal context
- Open-ended question that's easy to answer
- Encourage shares/saves subtly
- {hashtag_count} community hashtags
- Emojis: {emoji_style}

Caption:
"""
}

# Hashtag banks by category
HASHTAG_BANKS = {
    "lifestyle": [
        "#lifestyle", "#dailylife", "#aesthetic", "#vibes", "#mood",
        "#livingmybestlife", "#dayinthelife", "#currentmood", "#goodvibes",
        "#lifestyleblogger", "#aestheticlife", "#simplelife", "#slowliving"
    ],
    "fashion": [
        "#fashion", "#style", "#ootd", "#fashionista", "#streetstyle",
        "#fashionblogger", "#styleinspiration", "#outfitoftheday", "#fashionstyle",
        "#lookoftheday", "#fashiongram", "#styleinspo", "#whatiwore"
    ],
    "ai_influencer": [
        "#aiinfluencer", "#virtualinfluencer", "#digitalcreator", "#aiart",
        "#futureishere", "#virtualmodel", "#digitalart", "#aigenerated",
        "#metaverse", "#digitalinfluencer", "#virtualreality", "#techlife"
    ],
    "engagement": [
        "#communityovercompetition", "#letschat", "#questionoftheday",
        "#discussiontime", "#yourthoughts", "#talkingpoints", "#opinionswelcome"
    ]
}


def generate_caption(
    image_description: str,
    content_type: str = "lifestyle",
    platform: str = "instagram",
    additional_context: dict = None
) -> dict:
    """
    Generate a caption using AI.
    
    Args:
        image_description: Description of the image content
        content_type: Type of content (lifestyle, fashion, inspirational, product, engagement)
        platform: Target platform (instagram, tiktok, twitter)
        additional_context: Extra context for the prompt
        
    Returns:
        dict with caption, hashtags, and metadata
    """
    
    # Build the prompt
    template = CAPTION_TEMPLATES.get(content_type, CAPTION_TEMPLATES["lifestyle"])
    
    context = {
        **CHARACTER_CONFIG,
        "image_description": image_description,
        "values": ", ".join(CHARACTER_CONFIG["values"]),
        **(additional_context or {})
    }
    
    prompt = template.format(**context)
    
    # TODO: Uncomment and configure when you have API access
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # 
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": f"You are a social media expert writing captions for {CHARACTER_CONFIG['name']}, "
    #                       f"an AI influencer. Match their voice perfectly: {CHARACTER_CONFIG['personality']}"
    #         },
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.8,
    #     max_tokens=500
    # )
    # 
    # caption = response.choices[0].message.content
    
    # Placeholder response for demonstration
    caption = f"""✨ {image_description}

Sometimes the best moments are the ones you didn't plan for. 
Just another day of discovering new pixels and possibilities.

What's bringing you joy today? Drop it below 👇

.
.
.
{' '.join(HASHTAG_BANKS['lifestyle'][:10])}
{' '.join(HASHTAG_BANKS['ai_influencer'][:8])}
"""
    
    return {
        "caption": caption,
        "content_type": content_type,
        "platform": platform,
        "character": CHARACTER_CONFIG["name"],
        "generated_at": datetime.now().isoformat(),
        "word_count": len(caption.split()),
        "hashtag_count": caption.count("#")
    }


def generate_variants(
    image_description: str,
    content_type: str = "lifestyle",
    num_variants: int = 3
) -> list:
    """
    Generate multiple caption variants for A/B testing.
    """
    variants = []
    
    tones = ["playful", "thoughtful", "energetic"]
    
    for i in range(num_variants):
        # Modify context slightly for each variant
        context = {"mood": tones[i % len(tones)]}
        
        variant = generate_caption(
            image_description=image_description,
            content_type=content_type,
            additional_context=context
        )
        variant["variant_id"] = i + 1
        variant["tone_variant"] = tones[i % len(tones)]
        variants.append(variant)
    
    return variants


def save_caption(caption_data: dict, output_dir: str = "captions"):
    """Save generated caption to file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"caption_{timestamp}.json"
    
    with open(output_path / filename, "w") as f:
        json.dump(caption_data, f, indent=2)
    
    print(f"✅ Caption saved to {output_path / filename}")
    return output_path / filename


def main():
    parser = argparse.ArgumentParser(description="Generate AI influencer captions")
    parser.add_argument("--image", "-i", required=True, help="Image description or path")
    parser.add_argument("--type", "-t", default="lifestyle", 
                       choices=["lifestyle", "fashion", "inspirational", "product", "engagement"],
                       help="Content type")
    parser.add_argument("--platform", "-p", default="instagram",
                       choices=["instagram", "tiktok", "twitter"],
                       help="Target platform")
    parser.add_argument("--variants", "-v", type=int, default=1,
                       help="Number of caption variants to generate")
    parser.add_argument("--save", "-s", action="store_true",
                       help="Save caption to file")
    
    args = parser.parse_args()
    
    print(f"\n🤖 Generating caption for: {args.image}")
    print(f"   Type: {args.type} | Platform: {args.platform}\n")
    
    if args.variants > 1:
        results = generate_variants(args.image, args.type, args.variants)
        for i, result in enumerate(results):
            print(f"\n--- Variant {i+1} ({result['tone_variant']}) ---")
            print(result["caption"])
            if args.save:
                save_caption(result)
    else:
        result = generate_caption(args.image, args.type, args.platform)
        print("--- Generated Caption ---")
        print(result["caption"])
        if args.save:
            save_caption(result)


if __name__ == "__main__":
    main()
