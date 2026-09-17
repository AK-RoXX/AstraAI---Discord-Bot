import httpx
import feedparser
from urllib.parse import quote


ARXIV_URL = (
    "https://export.arxiv.org/api/query"
)


async def search_arxiv(
    query: str,
    max_results: int = 10,
):

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.get(
            ARXIV_URL,
            params=params,
        )

        response.raise_for_status()

    feed = feedparser.parse(
        response.text
    )

    papers = []

    for entry in feed.entries:

        papers.append({
            "title":
                entry.get(
                    "title",
                    ""
                ).replace("\n", " ").strip(),

            "summary":
                entry.get(
                    "summary",
                    ""
                ).replace("\n", " ").strip(),

            "authors": [
                a.name
                for a in entry.get(
                    "authors",
                    []
                )
            ],

            "url":
                entry.get(
                    "link",
                    ""
                ),

            "published":
                entry.get(
                    "published",
                    ""
                ),

            "updated":
                entry.get(
                    "updated",
                    ""
                ),
        })

    return papers