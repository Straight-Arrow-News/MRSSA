from datetime import datetime
from html import unescape

import httpx
from jinja2 import Environment as JinjaEnvironment

from src.utils import fetch_post_content, prepend_video_player


async def transform_api_data_to_feed_items(
    api_response: list, client: httpx.AsyncClient
) -> list:
    items = []
    for entry in api_response:
        video_id = entry.get("video_id")
        if not video_id:
            continue

        link = entry.get("link", "").replace("straightarrownews.com", "san.com")

        post_data = await fetch_post_content(link, client)

        if not link or not post_data["html"]:
            continue

        print(f"Processing video_id: {video_id}, link: {link}")

        print(
            f"Post data html length: {len(post_data['html'])}, author: {post_data['author']}"
        )

        bylines = entry.get("bylines", [])
        author = bylines[0].get("name") if bylines else post_data.get("author", "")

        video_data = entry.get("video", {})
        video_description = video_data.get("description", "")

        date_published = entry.get("date_gmt", "")
        pubdate_formatted = ""
        if date_published:
            dt = datetime.fromisoformat(date_published)
            dt_utc = dt.replace(tzinfo=None)
            pubdate_formatted = dt_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")

        featured_image = entry.get("featured_image", {})
        thumbnail_url = featured_image.get("url", "")

        title_data = entry.get("title", {})
        title_raw = (
            title_data.get("rendered", "") if isinstance(title_data, dict) else ""
        )
        title = unescape(title_raw)

        player_url = f"https://players.brightcove.net/6279053007001/vxzO09n2c_default/index.html?videoId={video_id}"

        content_html = post_data["html"].replace("\xa0", "&nbsp;")
        content_with_header = prepend_video_player(content_html, player_url)

        item = {
            "title": title,
            "link": link,
            "pubdate": pubdate_formatted,
            "description": video_description or title,
            "author": author,
            "content": content_with_header,
            "thumbnail_url": thumbnail_url,
        }
        items.append(item)

    return items


async def get_newsbreak_feed(
    templates: JinjaEnvironment,
    x_feed_url: str | None = None,
) -> str:
    api_url = "https://api.san.com/wp-json/wp/v2/sa_core_content/?san_v2&per_page=20"

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        items = await transform_api_data_to_feed_items(api_data, client)

    template_response = templates.get_template("newsbreak.j2").render(
        {"feed_url": x_feed_url or "", "items": items}
    )

    return template_response
