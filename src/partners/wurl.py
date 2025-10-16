import logging
from datetime import datetime
from html import unescape

import httpx
from jinja2 import Environment as JinjaEnvironment

from src.environment import BRIGHTCOVE_ACCOUNT_ID, BRIGHTCOVE_POLICY_KEY
from src.utils import fetch_post_content, get_video_info, prepend_video_player

logger = logging.getLogger(__name__)


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

        logger.info(f"Processing video_id: {video_id}, link: {link}")

        logger.info(
            f"Post data html length: {len(post_data['html'])}, author: {post_data['author']}"
        )

        bylines = entry.get("bylines", [])
        author = bylines[0].get("name") if bylines else post_data.get("author", "")

        video_data = entry.get("video", {})
        video_description = video_data.get("description", "")

        taxonomies = entry.get("taxonomies", {})
        keywords_list = []
        for tax_key in ["sa_type", "sa_issue"]:
            tax = taxonomies.get(tax_key, {})
            terms = tax.get("terms", [])
            for term in terms:
                slug = term.get("slug", "").replace("-", " ")
                keywords_list.append(slug)
        keywords_str = ",".join(keywords_list) if keywords_list else ""

        date_published = entry.get("date_gmt", "")
        pubdate_formatted = ""
        valid_start = ""
        if date_published:
            dt = datetime.fromisoformat(date_published)
            dt_utc = dt.replace(tzinfo=None)
            pubdate_formatted = dt_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
            valid_start = dt_utc.isoformat() + "Z"

        featured_image = entry.get("featured_image", {})
        thumbnail_url = featured_image.get("url", "")

        title_data = entry.get("title", {})
        title_raw = (
            title_data.get("rendered", "") if isinstance(title_data, dict) else ""
        )
        title = unescape(title_raw)

        guid = f"6279053007001:{video_id}"

        player_url = f"https://players.brightcove.net/6279053007001/8Qp6u0bJE_default/index.html?videoId={video_id}"

        content_html = post_data["html"].replace("\xa0", "&nbsp;")
        content_with_header = prepend_video_player(content_html, player_url)

        video_information = await get_video_info(
            video_id,
            BRIGHTCOVE_ACCOUNT_ID,
            BRIGHTCOVE_POLICY_KEY,
        )

        item = {
            "title": title,
            "guid": guid,
            "link": link,
            "pubdate": pubdate_formatted,
            "description": video_description or title,
            "author": author,
            "content": content_with_header,
            "valid_start": valid_start,
            "thumbnail_url": thumbnail_url,
            "content_url": video_information["content_url"],
            "duration": video_information["duration"],
            "bitrate": video_information["bitrate"],
            "keywords": keywords_str,
        }
        items.append(item)

    return items


async def get_wurl_feed(
    templates: JinjaEnvironment,
    x_feed_url: str | None = None,
) -> str:
    api_url = "https://api.san.com/wp-json/wp/v2/sa_core_content/?san_v2&per_page=20"

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        items = await transform_api_data_to_feed_items(api_data, client)

    logger.info(f"Successfully generated Wurl feed with {len(items)} items")
    template_response = templates.get_template("wurl.j2").render(
        {"feed_url": x_feed_url or "", "items": items}
    )

    return template_response
