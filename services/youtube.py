import os
import httpx

API_KEY = os.getenv("YOUTUBE_API_KEY", "")


async def recommend_videos(topic="agentic AI"):
    if not API_KEY:
        # Fallback links are search URLs, avoiding a fake claim about a specific video.
        from urllib.parse import quote_plus
        q = quote_plus(topic)
        return [
            {"title": f"YouTube search: {topic}", "channel": "YouTube", "url": f"https://www.youtube.com/results?search_query={q}"},
        ]

    params = {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "order": "relevance",
        "maxResults": 5,
        "relevanceLanguage": "en",
        "safeSearch": "moderate",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={**params, "key": API_KEY},
        )
        r.raise_for_status()
        data = r.json()

    results = []
    for item in data.get("items", []):
        vid = item.get("id", {}).get("videoId")
        if not vid:
            continue
        sn = item.get("snippet", {})
        results.append({
            "title": sn.get("title", ""),
            "channel": sn.get("channelTitle", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "published": sn.get("publishedAt", ""),
            "description": sn.get("description", "")[:500],
        })
    return results
