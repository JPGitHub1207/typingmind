"""
AI Influencer Analytics Tracker
Track engagement metrics, growth, and revenue across platforms.

Usage:
    python analytics_tracker.py --action dashboard
    python analytics_tracker.py --action report --period weekly
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import defaultdict

# Database path
DB_PATH = Path("data/analytics.db")


@dataclass
class DailyMetrics:
    date: str
    platform: str
    followers: int
    following: int
    posts: int
    likes: int
    comments: int
    shares: int
    saves: int
    reach: int
    impressions: int
    profile_visits: int
    website_clicks: int
    engagement_rate: float


@dataclass
class ContentMetrics:
    content_id: str
    platform: str
    content_type: str
    posted_at: datetime
    likes: int
    comments: int
    shares: int
    saves: int
    reach: int
    impressions: int
    engagement_rate: float


@dataclass
class RevenueEntry:
    date: str
    source: str  # sponsorship, affiliate, subscription, product
    brand: str
    amount: float
    currency: str
    status: str  # pending, paid, cancelled
    notes: str


def init_database():
    """Initialize analytics database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Daily metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            platform TEXT NOT NULL,
            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,
            posts INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            profile_visits INTEGER DEFAULT 0,
            website_clicks INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, platform)
        )
    """)
    
    # Content performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            content_type TEXT,
            posted_at TIMESTAMP,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            reach INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(content_id, platform)
        )
    """)
    
    # Revenue tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            source TEXT NOT NULL,
            brand TEXT,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Goals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            platform TEXT,
            target_value REAL NOT NULL,
            current_value REAL DEFAULT 0,
            deadline TEXT,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Analytics database initialized")


def log_daily_metrics(metrics: DailyMetrics):
    """Log daily metrics for a platform."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO daily_metrics 
        (date, platform, followers, following, posts, likes, comments, 
         shares, saves, reach, impressions, profile_visits, website_clicks, engagement_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metrics.date, metrics.platform, metrics.followers, metrics.following,
        metrics.posts, metrics.likes, metrics.comments, metrics.shares,
        metrics.saves, metrics.reach, metrics.impressions,
        metrics.profile_visits, metrics.website_clicks, metrics.engagement_rate
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ Logged metrics for {metrics.platform} on {metrics.date}")


def log_revenue(entry: RevenueEntry):
    """Log a revenue entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO revenue (date, source, brand, amount, currency, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.date, entry.source, entry.brand, entry.amount,
        entry.currency, entry.status, entry.notes
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ Logged revenue: ${entry.amount} from {entry.source}")


def calculate_engagement_rate(likes: int, comments: int, shares: int, saves: int, followers: int) -> float:
    """Calculate engagement rate."""
    if followers == 0:
        return 0.0
    total_engagement = likes + comments + shares + saves
    return round((total_engagement / followers) * 100, 2)


def get_growth_metrics(platform: str, days: int = 30) -> dict:
    """Get follower growth metrics for a period."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT date, followers FROM daily_metrics
        WHERE platform = ? AND date BETWEEN ? AND ?
        ORDER BY date
    """, (platform, start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) < 2:
        return {"error": "Not enough data"}
    
    start_followers = rows[0][1]
    end_followers = rows[-1][1]
    growth = end_followers - start_followers
    growth_rate = round((growth / start_followers) * 100, 2) if start_followers > 0 else 0
    
    # Calculate daily average growth
    daily_avg = growth / days if days > 0 else 0
    
    return {
        "platform": platform,
        "period_days": days,
        "start_followers": start_followers,
        "end_followers": end_followers,
        "total_growth": growth,
        "growth_rate_percent": growth_rate,
        "daily_average_growth": round(daily_avg, 1),
        "projected_30_day": round(daily_avg * 30),
        "projected_90_day": round(daily_avg * 90)
    }


def get_top_content(platform: str = None, limit: int = 10) -> List[dict]:
    """Get top performing content by engagement."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if platform:
        cursor.execute("""
            SELECT * FROM content_metrics
            WHERE platform = ?
            ORDER BY engagement_rate DESC
            LIMIT ?
        """, (platform, limit))
    else:
        cursor.execute("""
            SELECT * FROM content_metrics
            ORDER BY engagement_rate DESC
            LIMIT ?
        """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "content_id": row[1],
            "platform": row[2],
            "content_type": row[3],
            "likes": row[5],
            "comments": row[6],
            "shares": row[7],
            "saves": row[8],
            "engagement_rate": row[11]
        })
    
    return results


def get_revenue_summary(period: str = "monthly") -> dict:
    """Get revenue summary for a period."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if period == "weekly":
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    elif period == "monthly":
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    elif period == "yearly":
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    else:
        start_date = "2020-01-01"  # All time
    
    cursor.execute("""
        SELECT source, SUM(amount), COUNT(*) FROM revenue
        WHERE date >= ? AND status = 'paid'
        GROUP BY source
    """, (start_date,))
    
    by_source = {}
    total = 0
    for row in cursor.fetchall():
        by_source[row[0]] = {"amount": row[1], "count": row[2]}
        total += row[1]
    
    cursor.execute("""
        SELECT SUM(amount) FROM revenue
        WHERE date >= ? AND status = 'pending'
    """, (start_date,))
    
    pending = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "period": period,
        "total_earned": round(total, 2),
        "pending": round(pending, 2),
        "by_source": by_source,
        "average_deal": round(total / sum(v["count"] for v in by_source.values()), 2) if by_source else 0
    }


def generate_dashboard():
    """Generate a text-based analytics dashboard."""
    print("\n" + "=" * 70)
    print("📊 AI INFLUENCER ANALYTICS DASHBOARD")
    print("=" * 70)
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Follower Growth Section
    print("\n📈 FOLLOWER GROWTH (Last 30 Days)")
    print("-" * 50)
    
    for platform in ["instagram", "tiktok", "twitter"]:
        growth = get_growth_metrics(platform, 30)
        if "error" not in growth:
            trend = "📈" if growth["total_growth"] > 0 else "📉" if growth["total_growth"] < 0 else "➡️"
            print(f"\n   {platform.upper()}")
            print(f"   {trend} {growth['start_followers']:,} → {growth['end_followers']:,} ({growth['growth_rate_percent']:+.1f}%)")
            print(f"      Daily avg: +{growth['daily_average_growth']:.0f}")
            print(f"      Projected 90-day: +{growth['projected_90_day']:,}")
        else:
            print(f"\n   {platform.upper()}: No data available")
    
    # Revenue Section
    print("\n\n💰 REVENUE SUMMARY")
    print("-" * 50)
    
    for period in ["weekly", "monthly"]:
        rev = get_revenue_summary(period)
        print(f"\n   {period.upper()}")
        print(f"   Total Earned: ${rev['total_earned']:,.2f}")
        print(f"   Pending: ${rev['pending']:,.2f}")
        if rev['by_source']:
            print("   By Source:")
            for source, data in rev['by_source'].items():
                print(f"      - {source}: ${data['amount']:,.2f} ({data['count']} deals)")
    
    # Top Content Section
    print("\n\n🏆 TOP PERFORMING CONTENT")
    print("-" * 50)
    
    top_content = get_top_content(limit=5)
    if top_content:
        for i, content in enumerate(top_content, 1):
            print(f"\n   {i}. [{content['platform']}] {content['content_type']}")
            print(f"      Engagement: {content['engagement_rate']:.2f}%")
            print(f"      ❤️ {content['likes']:,} | 💬 {content['comments']:,} | 🔄 {content['shares']:,} | 📌 {content['saves']:,}")
    else:
        print("   No content data available yet")
    
    # Recommendations Section
    print("\n\n💡 RECOMMENDATIONS")
    print("-" * 50)
    print("   Based on your data:")
    print("   • Focus on content types with highest engagement")
    print("   • Post during optimal hours for your audience")
    print("   • Increase posting frequency on fastest-growing platform")
    print("   • Diversify revenue streams")
    
    print("\n" + "=" * 70)


def generate_report(period: str = "weekly", output_format: str = "text") -> str:
    """Generate a detailed report."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "period": period,
        "growth": {},
        "revenue": get_revenue_summary(period),
        "top_content": get_top_content(limit=10)
    }
    
    for platform in ["instagram", "tiktok", "twitter"]:
        days = 7 if period == "weekly" else 30 if period == "monthly" else 365
        report["growth"][platform] = get_growth_metrics(platform, days)
    
    if output_format == "json":
        return json.dumps(report, indent=2, default=str)
    
    # Text format
    lines = [
        f"📊 {period.upper()} ANALYTICS REPORT",
        f"Generated: {report['generated_at']}",
        "",
        "GROWTH SUMMARY:",
    ]
    
    for platform, data in report["growth"].items():
        if "error" not in data:
            lines.append(f"  {platform}: +{data['total_growth']:,} ({data['growth_rate_percent']:+.1f}%)")
    
    lines.extend([
        "",
        "REVENUE SUMMARY:",
        f"  Total: ${report['revenue']['total_earned']:,.2f}",
        f"  Pending: ${report['revenue']['pending']:,.2f}",
    ])
    
    return "\n".join(lines)


def add_sample_data():
    """Add sample data for demonstration."""
    today = datetime.now()
    
    # Sample daily metrics
    for i in range(30):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        base_followers = 10000 + (30 - i) * 150  # Growing trend
        
        metrics = DailyMetrics(
            date=date,
            platform="instagram",
            followers=base_followers + (i % 5) * 50,
            following=500,
            posts=150 + i,
            likes=500 + (i % 10) * 100,
            comments=50 + (i % 5) * 20,
            shares=20 + (i % 3) * 10,
            saves=30 + (i % 4) * 15,
            reach=base_followers * 2,
            impressions=base_followers * 3,
            profile_visits=100 + (i % 10) * 20,
            website_clicks=20 + (i % 5) * 5,
            engagement_rate=calculate_engagement_rate(500, 50, 20, 30, base_followers)
        )
        log_daily_metrics(metrics)
    
    # Sample revenue entries
    revenue_samples = [
        RevenueEntry("2024-01-15", "sponsorship", "Brand A", 500, "USD", "paid", "Instagram post"),
        RevenueEntry("2024-01-20", "affiliate", "Amazon", 125.50, "USD", "paid", "Tech products"),
        RevenueEntry("2024-01-25", "subscription", "Patreon", 340, "USD", "paid", "Monthly subs"),
        RevenueEntry("2024-02-01", "sponsorship", "Brand B", 750, "USD", "pending", "Reel + Stories"),
    ]
    
    for entry in revenue_samples:
        log_revenue(entry)
    
    print("✅ Sample data added")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Influencer Analytics Tracker")
    parser.add_argument("--action", "-a", required=True,
                       choices=["init", "dashboard", "report", "sample"],
                       help="Action to perform")
    parser.add_argument("--period", "-p", default="monthly",
                       choices=["weekly", "monthly", "yearly", "all"],
                       help="Report period")
    parser.add_argument("--format", "-f", default="text",
                       choices=["text", "json"],
                       help="Output format")
    parser.add_argument("--platform", help="Filter by platform")
    
    args = parser.parse_args()
    
    if args.action == "init":
        init_database()
        
    elif args.action == "dashboard":
        generate_dashboard()
        
    elif args.action == "report":
        report = generate_report(args.period, args.format)
        print(report)
        
    elif args.action == "sample":
        init_database()
        add_sample_data()


if __name__ == "__main__":
    main()
