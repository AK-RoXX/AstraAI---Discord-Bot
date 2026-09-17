import random
import httpx


ANILIST_URL = (
    "https://graphql.anilist.co"
)


QUERY = """
query ($page: Int) {

    Page(
        page: $page
        perPage: 20
    ) {

        media(
            type: ANIME
            isAdult: false
            sort: TRENDING_DESC
        ) {

            id

            title {
                romaji
                english
                native
            }

            coverImage {
                large
                extraLarge
            }

            bannerImage

            description(
                asHtml: false
            )

            genres

            episodes

            averageScore

            season

            seasonYear
        }
    }
}
"""


async def get_anime():

    page = random.randint(
        1,
        10
    )

    payload = {
        "query": QUERY,
        "variables": {
            "page": page
        }
    }

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.post(
            ANILIST_URL,
            json=payload,
            headers={
                "Content-Type":
                    "application/json",
                "Accept":
                    "application/json",
            }
        )

        response.raise_for_status()

        data = response.json()

    media = (
        data
        .get("data", {})
        .get("Page", {})
        .get("media", [])
    )

    if not media:
        return None

    return random.choice(media)