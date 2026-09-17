import httpx


async def get_anime_image():
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get("https://api.waifu.pics/sfw/waifu")
            r.raise_for_status()
            return r.json().get("url")
    except Exception:
        return None
