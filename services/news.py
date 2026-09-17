import asyncio
import feedparser
import httpx
from datetime import datetime

FEEDS = {
    "AI": [
        "https://huggingface.co/blog/feed.xml",
        "https://arxiv.org/rss/cs.AI",
        "https://arxiv.org/rss/cs.LG",
    ],
    "research": [
        "https://arxiv.org/rss/cs.AI",
        "https://arxiv.org/rss/cs.LG",
        "https://arxiv.org/rss/cs.CV",
    ],
    "technology": [
        "https://hnrss.org/frontpage",
        "https://huggingface.co/blog/feed.xml",
    ],
    "finance": [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^NSEI&region=IN&lang=en-IN"
    ],
    "sports": [
        "https://www.espn.com/espn/rss/news"
    ],
}


async def read_feed(url):
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(url)
            r.raise_for_status()
            return feedparser.parse(r.text)
    except Exception:
        return feedparser.parse("")


async def fetch_news(topic="AI", limit=8):
    urls = FEEDS.get(topic, FEEDS["AI"])
    feeds = await asyncio.gather(*(read_feed(u) for u in urls))
    items = []
    seen = set()

    for feed in feeds:
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link or link in seen:
                continue
            seen.add(link)
            published = entry.get("published", entry.get("updated", ""))
            items.append({
                "title": title,
                "link": link,
                "published": published,
                "summary": entry.get("summary", "")[:600],
            })

    return items[:limit]


def format_news_for_discord(topic, items):
    if not items:
        return f"📰 No fresh {topic} items were retrieved."

    text = f"📰 **{topic} Intelligence Briefing**\n\n"
    for i, item in enumerate(items, 1):
        text += f"**{i}. {item['title']}**\n{item['link']}\n"
        if item["published"]:
            text += f"_{item['published']}_\n"
        text += "\n"
    return text
