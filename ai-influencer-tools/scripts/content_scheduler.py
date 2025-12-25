"""
AI Influencer Content Scheduler
Manages content calendar, optimal posting times, and multi-platform scheduling.

Usage:
    python content_scheduler.py --action schedule --content content.json
    python content_scheduler.py --action view --week current
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum

# Database path
DB_PATH = Path("data/content_calendar.db")


class Platform(Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    YOUTUBE = "youtube"


class ContentStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    POSTED = "posted"
    FAILED = "failed"


@dataclass
class ContentItem:
    id: Optional[int]
    title: str
    caption: str
    media_path: str
    platform: str
    content_type: str
    scheduled_time: datetime
    status: str = "draft"
    hashtags: str = ""
    notes: str = ""
    engagement_score: Optional[float] = None
    created_at: datetime = None
    posted_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


# Optimal posting times by platform (in UTC)
# Adjust based on your audience timezone
OPTIMAL_TIMES = {
    "instagram": {
        "monday": ["11:00", "14:00", "19:00"],
        "tuesday": ["10:00", "14:00", "19:00"],
        "wednesday": ["11:00", "15:00", "19:00"],
        "thursday": ["10:00", "14:00", "19:00"],
        "friday": ["10:00", "14:00", "17:00"],
        "saturday": ["10:00", "13:00"],
        "sunday": ["10:00", "13:00", "19:00"]
    },
    "tiktok": {
        "monday": ["06:00", "10:00", "22:00"],
        "tuesday": ["09:00", "12:00", "19:00"],
        "wednesday": ["07:00", "11:00", "22:00"],
        "thursday": ["09:00", "12:00", "19:00"],
        "friday": ["05:00", "13:00", "15:00"],
        "saturday": ["11:00", "19:00", "21:00"],
        "sunday": ["08:00", "16:00", "22:00"]
    },
    "twitter": {
        "monday": ["08:00", "12:00", "17:00"],
        "tuesday": ["08:00", "12:00", "17:00"],
        "wednesday": ["09:00", "12:00", "17:00"],
        "thursday": ["08:00", "12:00", "17:00"],
        "friday": ["09:00", "12:00", "15:00"],
        "saturday": ["09:00", "12:00"],
        "sunday": ["09:00", "12:00"]
    }
}

# Content mix recommendations per week
WEEKLY_CONTENT_MIX = {
    "instagram": {
        "feed_posts": 4,
        "reels": 5,
        "stories": 14,  # 2 per day
        "carousels": 2
    },
    "tiktok": {
        "videos": 7  # 1 per day minimum
    },
    "twitter": {
        "tweets": 14,  # 2 per day
        "threads": 1
    }
}


def init_database():
    """Initialize the SQLite database for content tracking."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            caption TEXT,
            media_path TEXT,
            platform TEXT NOT NULL,
            content_type TEXT,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'draft',
            hashtags TEXT,
            notes TEXT,
            engagement_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            posted_at TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")


def schedule_content(content: ContentItem) -> int:
    """Add content to the schedule."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO content (title, caption, media_path, platform, content_type,
                           scheduled_time, status, hashtags, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        content.title,
        content.caption,
        content.media_path,
        content.platform,
        content.content_type,
        content.scheduled_time,
        "scheduled",
        content.hashtags,
        content.notes,
        content.created_at
    ))
    
    content_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Content scheduled: '{content.title}' for {content.scheduled_time}")
    return content_id


def get_next_optimal_slot(platform: str, content_type: str = None) -> datetime:
    """Find the next optimal posting time for a platform."""
    now = datetime.now()
    optimal = OPTIMAL_TIMES.get(platform, OPTIMAL_TIMES["instagram"])
    
    # Check next 7 days
    for day_offset in range(7):
        check_date = now + timedelta(days=day_offset)
        day_name = check_date.strftime("%A").lower()
        
        if day_name in optimal:
            for time_str in optimal[day_name]:
                hour, minute = map(int, time_str.split(":"))
                slot_time = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Skip if time has passed today
                if slot_time > now:
                    # Check if slot is already taken
                    if not is_slot_taken(platform, slot_time):
                        return slot_time
    
    # Fallback: tomorrow at noon
    return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)


def is_slot_taken(platform: str, time: datetime, buffer_minutes: int = 60) -> bool:
    """Check if a time slot is already taken."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    buffer = timedelta(minutes=buffer_minutes)
    start_time = time - buffer
    end_time = time + buffer
    
    cursor.execute("""
        SELECT COUNT(*) FROM content 
        WHERE platform = ? 
        AND scheduled_time BETWEEN ? AND ?
        AND status IN ('scheduled', 'posted')
    """, (platform, start_time, end_time))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0


def get_weekly_schedule(week_offset: int = 0) -> dict:
    """Get content scheduled for a specific week."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate week boundaries
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=7)
    
    cursor.execute("""
        SELECT * FROM content 
        WHERE scheduled_time BETWEEN ? AND ?
        ORDER BY scheduled_time
    """, (start_of_week, end_of_week))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Organize by day
    schedule = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    
    for row in rows:
        content = {
            "id": row[0],
            "title": row[1],
            "platform": row[4],
            "content_type": row[5],
            "scheduled_time": row[6],
            "status": row[7]
        }
        scheduled = datetime.fromisoformat(row[6]) if row[6] else None
        if scheduled:
            day_name = scheduled.strftime("%A")
            schedule[day_name].append(content)
    
    return schedule


def view_calendar(week_offset: int = 0):
    """Display the content calendar in a readable format."""
    schedule = get_weekly_schedule(week_offset)
    
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    
    week_label = "Current Week" if week_offset == 0 else f"Week {'+' if week_offset > 0 else ''}{week_offset}"
    print(f"\n📅 Content Calendar - {week_label}")
    print(f"   {start_of_week.strftime('%B %d')} - {(start_of_week + timedelta(days=6)).strftime('%B %d, %Y')}")
    print("=" * 60)
    
    platform_emoji = {
        "instagram": "📸",
        "tiktok": "🎵",
        "twitter": "🐦",
        "youtube": "🎬"
    }
    
    status_emoji = {
        "draft": "📝",
        "scheduled": "⏰",
        "posted": "✅",
        "failed": "❌"
    }
    
    for day, items in schedule.items():
        day_date = start_of_week + timedelta(days=list(schedule.keys()).index(day))
        is_today = day_date.date() == today.date()
        
        day_marker = "👉 " if is_today else "   "
        print(f"\n{day_marker}{day} ({day_date.strftime('%m/%d')})")
        
        if not items:
            print("      - No content scheduled")
        else:
            for item in items:
                p_emoji = platform_emoji.get(item["platform"], "📱")
                s_emoji = status_emoji.get(item["status"], "❓")
                time_str = datetime.fromisoformat(item["scheduled_time"]).strftime("%H:%M")
                print(f"      {s_emoji} {time_str} | {p_emoji} {item['platform']}: {item['title'][:30]}...")


def get_content_gaps() -> dict:
    """Analyze the current week for content gaps based on recommendations."""
    schedule = get_weekly_schedule(0)  # Current week
    
    # Count content by platform and type
    counts = {}
    for day, items in schedule.items():
        for item in items:
            platform = item["platform"]
            content_type = item.get("content_type", "other")
            
            if platform not in counts:
                counts[platform] = {}
            if content_type not in counts[platform]:
                counts[platform][content_type] = 0
            counts[platform][content_type] += 1
    
    # Compare against recommendations
    gaps = {}
    for platform, recommendations in WEEKLY_CONTENT_MIX.items():
        gaps[platform] = {}
        for content_type, target in recommendations.items():
            current = counts.get(platform, {}).get(content_type, 0)
            if current < target:
                gaps[platform][content_type] = target - current
    
    return gaps


def suggest_content_plan() -> List[dict]:
    """Generate content suggestions based on gaps and optimal times."""
    gaps = get_content_gaps()
    suggestions = []
    
    for platform, content_gaps in gaps.items():
        for content_type, needed in content_gaps.items():
            for i in range(needed):
                optimal_time = get_next_optimal_slot(platform, content_type)
                suggestions.append({
                    "platform": platform,
                    "content_type": content_type,
                    "suggested_time": optimal_time.isoformat(),
                    "priority": "high" if needed > 2 else "medium"
                })
    
    return suggestions


def batch_schedule_from_file(file_path: str):
    """Schedule multiple content items from a JSON file."""
    with open(file_path, "r") as f:
        items = json.load(f)
    
    scheduled_count = 0
    for item in items:
        content = ContentItem(
            id=None,
            title=item["title"],
            caption=item.get("caption", ""),
            media_path=item.get("media_path", ""),
            platform=item["platform"],
            content_type=item.get("content_type", "post"),
            scheduled_time=datetime.fromisoformat(item["scheduled_time"]) if "scheduled_time" in item else get_next_optimal_slot(item["platform"]),
            hashtags=item.get("hashtags", ""),
            notes=item.get("notes", "")
        )
        schedule_content(content)
        scheduled_count += 1
    
    print(f"\n✅ Scheduled {scheduled_count} content items")


def export_schedule(output_path: str = "exports/schedule.json"):
    """Export current schedule to JSON."""
    schedule = get_weekly_schedule(0)
    
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, "w") as f:
        json.dump(schedule, f, indent=2, default=str)
    
    print(f"✅ Schedule exported to {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Influencer Content Scheduler")
    parser.add_argument("--action", "-a", required=True,
                       choices=["init", "schedule", "view", "gaps", "suggest", "export"],
                       help="Action to perform")
    parser.add_argument("--content", "-c", help="Path to content JSON file")
    parser.add_argument("--week", "-w", type=int, default=0,
                       help="Week offset (0=current, 1=next, -1=previous)")
    parser.add_argument("--platform", "-p", help="Filter by platform")
    
    args = parser.parse_args()
    
    if args.action == "init":
        init_database()
        
    elif args.action == "schedule":
        if args.content:
            batch_schedule_from_file(args.content)
        else:
            print("❌ Please provide content file with --content")
            
    elif args.action == "view":
        view_calendar(args.week)
        
    elif args.action == "gaps":
        gaps = get_content_gaps()
        print("\n📊 Content Gaps This Week")
        print("=" * 40)
        for platform, content_gaps in gaps.items():
            if content_gaps:
                print(f"\n{platform.upper()}:")
                for content_type, needed in content_gaps.items():
                    print(f"  - Need {needed} more {content_type}")
                    
    elif args.action == "suggest":
        suggestions = suggest_content_plan()
        print("\n💡 Content Suggestions")
        print("=" * 40)
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"\n{i}. {suggestion['platform']} - {suggestion['content_type']}")
            print(f"   Suggested time: {suggestion['suggested_time']}")
            print(f"   Priority: {suggestion['priority']}")
            
    elif args.action == "export":
        export_schedule()


if __name__ == "__main__":
    main()
