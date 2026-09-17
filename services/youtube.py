import os
import httpx


API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)


async def search_youtube(
    query: str,
    max_results: int = 10,
):

    if not API_KEY:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not configured."
        )

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "relevance",
        "maxResults": max_results,
        "relevanceLanguage": "en",
        "regionCode": "IN",
        "safeSearch": "moderate",
    }

    async with httpx.AsyncClient(
        timeout=20
    ) as client:

        response = await client.get(
            YOUTUBE_SEARCH_URL,
            params={
                **params,
                "key": API_KEY,
            },
        )

        response.raise_for_status()

        data = response.json()

    videos = []

    for item in data.get("items", []):

        video_id = (
            item
            .get("id", {})
            .get("videoId")
        )

        if not video_id:
            continue

        snippet = item.get(
            "snippet",
            {}
        )

        videos.append({
            "id": video_id,
            "title": snippet.get(
                "title",
                ""
            ),
            "description": snippet.get(
                "description",
                ""
            ),
            "channel": snippet.get(
                "channelTitle",
                ""
            ),
            "published": snippet.get(
                "publishedAt",
                ""
            ),
            "url":
                f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail":
                snippet.get(
                    "thumbnails",
                    {}
                ).get(
                    "high",
                    {}
                ).get(
                    "url"
                ),
        })

    return videos