import logging
from html import unescape

from src.brightcove import get_video_info, prepend_video_player
from src.environment import BRIGHTCOVE_ACCOUNT_ID, BRIGHTCOVE_POLICY_KEY
from src.wp import fetch_videos, format_date, parse_content

logger = logging.getLogger(__name__)

async def transform_api_data_to_feed_items(
    api_response: list,
    options: dict
) -> list:
    player_id = options.get("player_id", "")
    use_video_source = options.get("use_video_source", False)
    items = []
    logger.info("Looking through %s items", len(api_response))
    for entry in api_response:
        video_id = entry.get("video", {}).get("id")
        if not video_id:
            continue

        link = entry.get("link", "").replace("straightarrownews.com", "san.com")

        player_url = f"https://players.brightcove.net/{BRIGHTCOVE_ACCOUNT_ID}/{player_id}/index.html?videoId={video_id}"

        content_html = parse_content(entry.get("content", {}).get("rendered", ""))
        content_with_header = prepend_video_player(content_html, player_url)

        title_data = entry.get("title", {})
        title_raw = (
            title_data.get("rendered", "") if isinstance(title_data, dict) else ""
        )
        title = unescape(title_raw)

        pubdate_formatted, valid_start = format_date(entry.get("date_gmt", ""))

        terms = entry.get("taxonomies", {}).get("sa_issue", {}).get("terms", [])
        tags = [term.get("slug", "") for term in terms]


        item = {
            "title": title,
            "guid": f"6279053007001:{video_id}",
            "link": link,
            "pubdate": pubdate_formatted,
            "description": entry.get("video", {"description": ""}).get("description", ""),
            "author": entry.get("bylines", [""])[0].get("name", ""),
            "content": content_with_header,
            "valid_start": valid_start,
            "thumbnail_url": entry.get("featured_image", {"url": ""}).get("url", ""),
            "keywords": ",".join(tags) if tags else "",
        }
        if use_video_source:
            video_information = await get_video_info(
                video_id,
                BRIGHTCOVE_ACCOUNT_ID,
                BRIGHTCOVE_POLICY_KEY,
            )

            item["content_url"] = video_information["content_url"]
            item["duration"] = video_information["duration"]
            item["bitrate"] = video_information["bitrate"]
        else:
            item["player_url"] = player_url

        items.append(item)

    return items


async def build_model(options: dict) -> str:
    logger.info("Fetching video data")
    video_data = await fetch_videos()
    items = await transform_api_data_to_feed_items(video_data, options)
    return items
