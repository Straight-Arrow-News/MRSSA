import httpx


async def get_yahoo_articles_feed(x_feed_url: str | None = None) -> str:
    source_url = "https://san.com/simplefeed_msn_articles"

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(source_url)
        response.raise_for_status()
        content = response.text

    if x_feed_url:
        content = content.replace(
            '<atom:link href="https://san.com/simplefeed_msn_articles" rel="self" type="application/rss+xml" />',
            f'<atom:link href="{x_feed_url}" rel="self" type="application/rss+xml" />',
        )

    return content
