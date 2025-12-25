# 🤖 AI Influencer Tools

A collection of Python tools to help manage and automate your AI influencer business.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai-influencer-tools
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Add your API keys:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### 3. Initialize Databases

```bash
python scripts/content_scheduler.py --action init
python scripts/analytics_tracker.py --action init
```

## 📁 Project Structure

```
ai-influencer-tools/
├── config/
│   └── character_config.json    # Your AI character definition
├── scripts/
│   ├── caption_generator.py     # Generate on-brand captions
│   ├── content_scheduler.py     # Schedule & manage content
│   └── analytics_tracker.py     # Track metrics & revenue
├── data/                        # SQLite databases (auto-created)
├── assets/                      # Media files
│   ├── images/
│   ├── videos/
│   └── templates/
├── exports/                     # Generated reports
├── requirements.txt
└── README.md
```

## 🛠️ Tools Overview

### Caption Generator

Generate AI-powered captions that match your character's voice.

```bash
# Basic usage
python scripts/caption_generator.py --image "sunset beach photo" --type lifestyle

# Generate multiple variants for A/B testing
python scripts/caption_generator.py --image "new outfit reveal" --type fashion --variants 3

# Save to file
python scripts/caption_generator.py --image "inspirational moment" --type inspirational --save
```

**Content Types:**
- `lifestyle` - General life moments
- `fashion` - Outfit and style posts
- `inspirational` - Motivational content
- `product` - Sponsored/affiliate posts
- `engagement` - Discussion starters

### Content Scheduler

Plan and manage your content calendar across platforms.

```bash
# Initialize database
python scripts/content_scheduler.py --action init

# View current week's schedule
python scripts/content_scheduler.py --action view

# View next week
python scripts/content_scheduler.py --action view --week 1

# Find content gaps
python scripts/content_scheduler.py --action gaps

# Get posting suggestions
python scripts/content_scheduler.py --action suggest

# Schedule from JSON file
python scripts/content_scheduler.py --action schedule --content my_content.json

# Export schedule
python scripts/content_scheduler.py --action export
```

**Content JSON Format:**

```json
[
  {
    "title": "Monday morning vibes",
    "caption": "Starting the week with good energy ✨",
    "media_path": "assets/images/monday_001.png",
    "platform": "instagram",
    "content_type": "feed_post",
    "scheduled_time": "2024-02-05T10:00:00",
    "hashtags": "#mondaymotivation #newweek",
    "notes": "Use warm filter"
  }
]
```

### Analytics Tracker

Monitor your growth, engagement, and revenue.

```bash
# Initialize database
python scripts/analytics_tracker.py --action init

# View dashboard
python scripts/analytics_tracker.py --action dashboard

# Generate report
python scripts/analytics_tracker.py --action report --period weekly
python scripts/analytics_tracker.py --action report --period monthly --format json

# Add sample data (for testing)
python scripts/analytics_tracker.py --action sample
```

## 📊 Metrics Tracked

### Growth Metrics
- Followers / Following
- Daily/weekly/monthly growth rate
- Growth projections

### Engagement Metrics
- Likes, comments, shares, saves
- Engagement rate
- Reach and impressions
- Profile visits

### Revenue
- Sponsorship deals
- Affiliate earnings
- Subscription income
- Product sales

## 🎨 Character Configuration

Edit `config/character_config.json` to customize:

- **Personality traits** - How your character behaves
- **Visual identity** - Appearance and style
- **Content pillars** - What topics you cover
- **Prompt templates** - For consistent image generation

## 🔜 Coming Soon

- [ ] Instagram API integration (auto-posting)
- [ ] TikTok scheduling
- [ ] Image consistency checker
- [ ] Engagement response suggester
- [ ] Brand partnership tracker
- [ ] A/B test analyzer
- [ ] Web dashboard

## 💡 Tips for Success

1. **Consistency is key** - Post regularly using the scheduler
2. **Track everything** - Log metrics daily for accurate insights
3. **Test captions** - Use variants to find what resonates
4. **Stay on-brand** - Reference character config in all content
5. **Engage authentically** - Reply to comments daily

## 🤝 Contributing

Feel free to extend these tools! Some ideas:
- Add more caption templates
- Integrate with more platforms
- Build a web dashboard
- Add image generation integration

## 📄 License

MIT License - Use freely for your AI influencer venture!

---

**Need help?** Check the main strategy document: `AI_INFLUENCER_STRATEGY.md`
