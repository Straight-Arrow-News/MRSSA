import logging
import json
from datetime import datetime
from html import unescape

import httpx
from jinja2 import Environment as JinjaEnvironment

from bs4 import BeautifulSoup

from src.environment import BRIGHTCOVE_ACCOUNT_ID, BRIGHTCOVE_POLICY_KEY
from src.utils import fetch_post_content, get_video_info, prepend_video_player
from src.wp import fetch_videos

logger = logging.getLogger(__name__)


async def transform_api_data_to_feed_items(
    api_response: list
) -> list:
    items = []
    logger.info("Looking through %s items", len(api_response))
    for entry in api_response:
        video_id = entry.get("video", {}).get("id")
        if not video_id:
            continue

        link = entry.get("link", "").replace("straightarrownews.com", "san.com")

        # post_data = await fetch_post_content(link, client)

        # if not link or not post_data["html"]:
        #     continue

        # logger.info(f"Processing video_id: {video_id}, link: {link}")

        # logger.info(
        #     f"Post data html length: {len(post_data['html'])}, author: {post_data['author']}"
        # )

        post_data = BeautifulSoup(
            entry.get("content", {}).get("rendered", ""),
            "html.parser"
        )
        dl_block = post_data.find("div", class_="wp-block-san-app-download")
        if dl_block:
            dl_block.decompose()

        newsletter_block = post_data.find("div", class_="wp-block-san-san-inarticle-newsletter-signup")
        if newsletter_block:
            newsletter_block.decompose()

        social_block = post_data.find("div", class_="wp-block-san-san-inarticle-social-share")
        if social_block:
            social_block.decompose()

        # logger.info(post_data.prettify())
        # logger.info(str(post_data).replace('\n', '').replace('\r', ''))

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

        player_url = f"https://players.brightcove.net/6279053007001/9npVofANy_default/index.html?videoId={video_id}"

        # content_html = post_data["html"].replace("\xa0", "&nbsp;")
        content_html = str(post_data).replace('\n', '').replace('\r', '')
        content_with_header = prepend_video_player(content_html, player_url)

        video_information = await get_video_info(
            video_id,
            BRIGHTCOVE_ACCOUNT_ID,
            BRIGHTCOVE_POLICY_KEY,
        )

        terms = entry.get("taxonomies", {}).get("sa_issue", {}).get("terms", [])
        tags = [term.get("slug", "") for term in terms]


        ## TODO: make sure author is "position": "Producer"
        author = entry.get("bylines", [])[0].get("name", "")

        item = {
            "title": title,
            "guid": guid,
            "link": link,
            "pubdate": pubdate_formatted,
            "description": title,
            "author": author,
            "content": content_with_header,
            "valid_start": valid_start,
            "thumbnail_url": thumbnail_url,
            "content_url": video_information["content_url"],
            "duration": video_information["duration"],
            "bitrate": video_information["bitrate"],
            "keywords": tags,
        }
        items.append(item)

    return items


async def get_simplefeed_msn_feed(
    templates: JinjaEnvironment,
    x_feed_url: str | None = None,
) -> str:
    # api_url = "https://api.san.com/wp-json/wp/v2/sa_core_content/?san_v2&per_page=20"
    # async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
    #     response = await client.get(api_url)
    #     response.raise_for_status()
    #     api_data = response.json()

    #     items = await transform_api_data_to_feed_items(api_data, client)
    logger.info("Fetching video data")
    video_data = await fetch_videos()
    items = await transform_api_data_to_feed_items(video_data )

    logger.info(f"Successfully generated SimpleFeed MSN feed with {len(items)} items")
    template_response = templates.get_template("simplefeed-msn.j2").render(
        {"feed_url": x_feed_url or "", "items": items}
    )

    return template_response
