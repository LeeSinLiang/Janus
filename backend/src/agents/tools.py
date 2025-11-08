"""
Low-level tools for the multi-agent system.
These are the foundational tools that agents use to interact with external services.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from langchain_core.tools import tool


# Path to placeholder data
DATA_DIR = Path(__file__).parent / "data"
METRICS_FILE = DATA_DIR / "placeholder_metrics.json"


def load_placeholder_metrics() -> Dict[str, Any]:
    """Load placeholder metrics from JSON file"""
    with open(METRICS_FILE, 'r') as f:
        return json.load(f)


# =====================
# X (Twitter) API Tools
# =====================

@tool
def post_tweet(content: str, scheduled_time: Optional[str] = None) -> str:
    """
    Post a tweet to X (Twitter).

    Args:
        content: Tweet content (max 280 characters)
        scheduled_time: Optional ISO format datetime for scheduling

    Returns:
        Status message with tweet ID
    """
    if len(content) > 280:
        return f"Error: Tweet exceeds 280 characters ({len(content)} chars)"

    # Placeholder implementation
    tweet_id = f"tweet_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if scheduled_time:
        return f"✅ Tweet scheduled for {scheduled_time}. ID: {tweet_id}\nContent: {content}"
    else:
        return f"✅ Tweet posted successfully! ID: {tweet_id}\nContent: {content}"


@tool
def get_tweet_metrics(tweet_id: str) -> str:
    """
    Get metrics for a specific tweet.

    Args:
        tweet_id: The ID of the tweet

    Returns:
        JSON string with tweet metrics
    """
    # Load placeholder data
    data = load_placeholder_metrics()

    # Search for the tweet
    for tweet in data.get("tweets", []):
        if tweet["tweet_id"] == tweet_id:
            metrics = tweet["metrics"]
            return json.dumps({
                "tweet_id": tweet_id,
                "views": metrics["views"],
                "likes": metrics["likes"],
                "retweets": metrics["retweets"],
                "replies": metrics["replies"],
                "engagement_rate": metrics["engagement_rate"],
                "posted_at": tweet["posted_at"]
            }, indent=2)

    # Return sample metrics if tweet not found
    return json.dumps({
        "tweet_id": tweet_id,
        "views": 1500,
        "likes": 45,
        "retweets": 12,
        "replies": 8,
        "engagement_rate": 4.3,
        "posted_at": datetime.now().isoformat()
    }, indent=2)


@tool
def schedule_tweet(content: str, scheduled_time: str) -> str:
    """
    Schedule a tweet for future posting.

    Args:
        content: Tweet content (max 280 characters)
        scheduled_time: ISO format datetime (e.g., '2025-11-08T14:00:00Z')

    Returns:
        Confirmation message
    """
    if len(content) > 280:
        return f"Error: Tweet exceeds 280 characters ({len(content)} chars)"

    try:
        # Validate datetime format
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        tweet_id = f"tweet_scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return f"✅ Tweet scheduled for {scheduled_dt.strftime('%Y-%m-%d %H:%M UTC')}\nID: {tweet_id}\nContent: {content}"
    except ValueError as e:
        return f"Error: Invalid datetime format. Use ISO format (e.g., '2025-11-08T14:00:00Z')"


@tool
def validate_tweet_format(content: str) -> str:
    """
    Validate tweet content format and provide suggestions.

    Args:
        content: Tweet content to validate

    Returns:
        Validation result and suggestions
    """
    issues = []
    suggestions = []

    # Check length
    if len(content) > 280:
        issues.append(f"Tweet exceeds 280 characters ({len(content)} chars)")
        suggestions.append(f"Reduce by {len(content) - 280} characters")
    elif len(content) < 50:
        suggestions.append("Short tweets may get less engagement. Consider 100-200 chars for optimal engagement.")

    # Check for URLs without shortening
    if "http://" in content or "https://" in content:
        suggestions.append("URLs will be auto-shortened by X to ~23 characters")

    # Check for emojis
    emoji_count = sum(1 for char in content if ord(char) > 127)
    if emoji_count == 0:
        suggestions.append("Consider adding emojis - they increase engagement by ~45%")

    # Check for hashtags
    hashtag_count = content.count('#')
    if hashtag_count == 0:
        suggestions.append("Consider adding 1-2 relevant hashtags for discoverability")
    elif hashtag_count > 3:
        suggestions.append("Too many hashtags - limit to 2-3 for best engagement")

    if issues:
        return f"❌ Validation failed:\n" + "\n".join(f"- {issue}" for issue in issues)
    else:
        result = "✅ Tweet format is valid!\n"
        if suggestions:
            result += "\n💡 Suggestions:\n" + "\n".join(f"- {s}" for s in suggestions)
        return result


# ===================
# Metrics Tools
# ===================

@tool
def fetch_platform_metrics(platform: str = "x") -> str:
    """
    Fetch overall platform metrics and insights.

    Args:
        platform: Platform name (default: "x" for Twitter/X)

    Returns:
        JSON string with platform insights
    """
    data = load_placeholder_metrics()
    insights = data.get("platform_insights", {})

    return json.dumps({
        "platform": platform,
        "best_posting_times": insights.get("best_posting_times", []),
        "trending_topics": insights.get("trending_topics", []),
        "audience_active_hours": insights.get("audience_active_hours", {}),
        "competitor_benchmarks": insights.get("competitor_benchmarks", {})
    }, indent=2)


@tool
def calculate_engagement_rate(views: int, likes: int, retweets: int, replies: int) -> str:
    """
    Calculate engagement rate from metrics.

    Args:
        views: Number of views
        likes: Number of likes
        retweets: Number of retweets
        replies: Number of replies

    Returns:
        Engagement rate calculation
    """
    if views == 0:
        return "Error: Views cannot be zero"

    total_engagement = likes + retweets + replies
    engagement_rate = (total_engagement / views) * 100

    # Provide context
    if engagement_rate >= 3.5:
        performance = "Excellent"
    elif engagement_rate >= 2.5:
        performance = "Good"
    elif engagement_rate >= 1.5:
        performance = "Average"
    else:
        performance = "Below Average"

    return json.dumps({
        "engagement_rate": round(engagement_rate, 2),
        "total_engagement": total_engagement,
        "views": views,
        "performance": performance,
        "industry_avg": 2.5
    }, indent=2)


@tool
def get_content_performance_insights() -> str:
    """
    Get insights about content performance patterns.

    Returns:
        JSON string with content performance data
    """
    data = load_placeholder_metrics()
    performance = data.get("content_performance", {})

    return json.dumps({
        "top_performing_formats": performance.get("top_performing_formats", []),
        "optimal_content_length": performance.get("optimal_content_length", {}),
        "emoji_impact": performance.get("emoji_impact", {}),
        "recommendation": "Medium-length tweets (100-200 chars) with emojis and thread format perform best"
    }, indent=2)


@tool
def analyze_audience_sentiment(tweet_id: str) -> str:
    """
    Analyze sentiment from tweet comments and engagement.

    Args:
        tweet_id: The ID of the tweet to analyze

    Returns:
        JSON string with sentiment analysis
    """
    data = load_placeholder_metrics()

    # Search for the tweet
    for tweet in data.get("tweets", []):
        if tweet["tweet_id"] == tweet_id:
            comments = tweet.get("comments", [])

            # Count sentiments
            sentiments = {"positive": 0, "neutral": 0, "negative": 0}
            topics_mentioned = []

            for comment in comments:
                sentiment = comment.get("sentiment", "neutral")
                sentiments[sentiment] += 1
                topics_mentioned.extend(comment.get("mentions_topic", []))

            total = sum(sentiments.values())
            sentiment_percentages = {
                k: round((v / total * 100), 1) if total > 0 else 0
                for k, v in sentiments.items()
            }

            return json.dumps({
                "tweet_id": tweet_id,
                "overall_sentiment": tweet.get("audience_insights", {}).get("sentiment", "neutral"),
                "sentiment_breakdown": sentiment_percentages,
                "common_topics": list(set(topics_mentioned)),
                "total_comments_analyzed": total
            }, indent=2)

    # Default response
    return json.dumps({
        "tweet_id": tweet_id,
        "overall_sentiment": "positive",
        "sentiment_breakdown": {"positive": 70.0, "neutral": 25.0, "negative": 5.0},
        "common_topics": ["interest", "features"],
        "total_comments_analyzed": 10
    }, indent=2)


@tool
def get_optimal_posting_time(day_type: str = "weekday") -> str:
    """
    Get optimal posting times based on historical data.

    Args:
        day_type: "weekday" or "weekend"

    Returns:
        Recommended posting times
    """
    data = load_placeholder_metrics()
    insights = data.get("platform_insights", {})

    best_times = insights.get("best_posting_times", [])
    filtered_times = [t for t in best_times if t["day"] == day_type]

    # Sort by engagement
    filtered_times.sort(key=lambda x: x["avg_engagement"], reverse=True)

    if filtered_times:
        top_time = filtered_times[0]
        return json.dumps({
            "day_type": day_type,
            "best_hour": top_time["hour"],
            "avg_engagement": top_time["avg_engagement"],
            "all_good_times": [f"{t['hour']}:00" for t in filtered_times[:3]],
            "recommendation": f"Post around {top_time['hour']}:00 for best engagement"
        }, indent=2)

    return json.dumps({
        "day_type": day_type,
        "best_hour": 14,
        "recommendation": "14:00 (2 PM) is generally a good time"
    }, indent=2)


# ===================
# Content Tools
# ===================

@tool
def generate_hashtags(topic: str, max_count: int = 3) -> str:
    """
    Generate relevant hashtags for a topic.

    Args:
        topic: The topic or content theme
        max_count: Maximum number of hashtags (default: 3)

    Returns:
        List of suggested hashtags
    """
    # Placeholder hashtag generation based on topic keywords
    hashtag_map = {
        "ai": ["#AI", "#ArtificialIntelligence", "#MachineLearning", "#Tech"],
        "startup": ["#Startup", "#Entrepreneur", "#Founders", "#StartupLife"],
        "marketing": ["#Marketing", "#DigitalMarketing", "#GrowthHacking", "#MarketingTips"],
        "product": ["#ProductLaunch", "#Product", "#Innovation", "#NewProduct"],
        "saas": ["#SaaS", "#CloudComputing", "#B2B", "#SoftwareDevelopment"]
    }

    topic_lower = topic.lower()
    hashtags = []

    for key, tags in hashtag_map.items():
        if key in topic_lower:
            hashtags.extend(tags[:max_count])

    # Default hashtags if no match
    if not hashtags:
        hashtags = ["#Tech", "#Innovation", "#Business"]

    return " ".join(hashtags[:max_count])
