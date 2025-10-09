from datetime import datetime
from html import unescape
from xml.etree import ElementTree as ET

import httpx
from jinja2 import Environment as JinjaEnvironment


async def fetch_post_content(link: str, client: httpx.AsyncClient) -> dict:
    if not link or not (
        "https://straightarrownews.com/cc/" in link or "https://san.com/cc/" in link
    ):
        return {"html": "", "author": "", "title": ""}

    feed_url = f"{link}feed?withoutcomments=1"
    try:
        response = await client.get(feed_url)
        response.raise_for_status()
        xml_data = response.text

        root = ET.fromstring(xml_data)
        item = root.find(".//item")

        if item is None:
            return {"html": "", "author": "", "title": ""}

        creator = item.find(".//{http://purl.org/dc/elements/1.1/}creator")
        author = creator.text if creator is not None else ""

        encoded = item.find(".//{http://purl.org/rss/1.0/modules/content/}encoded")
        html = encoded.text if encoded is not None else ""

        title_elem = item.find(".//title")
        title = title_elem.text if title_elem is not None else ""

        return {"html": html, "author": author, "title": title}
    except Exception:
        return {"html": "", "author": "", "title": ""}


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

        player_url = f"https://players.brightcove.net/6279053007001/TcfN150bWH_default/index.html?videoId={video_id}"

        guid = f"6279053007001:{video_id}"

        content_html = (
            post_data["html"]
            .replace(
                'src="https://players.brightcove.net/6279053007001/Jkljh8LEJ_default/index.html?videoId=',
                'src="https://players.brightcove.net/6279053007001/TcfN150bWH_default/index.html?videoId=',
            )
            .replace("\xa0", "&nbsp;")
        )

        path = link.replace("https://san.com", "")

        item = {
            "title": title,
            "guid": guid,
            "link": link,
            "pubdate": pubdate_formatted,
            "description": video_description or title,
            "author": author,
            "content": content_html,
            "valid_start": valid_start,
            "thumbnail_url": thumbnail_url,
            "player_url": player_url,
            "keywords": keywords_str,
            "path": path,
        }
        items.append(item)

    return items


async def get_smart_news_feed(
    templates: JinjaEnvironment,
    x_feed_url: str | None = None,
) -> str:
    api_url = "https://api.san.com/wp-json/wp/v2/sa_core_content/?san_v2&per_page=20"

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        items = await transform_api_data_to_feed_items(api_data, client)

    template_response = templates.get_template("smart-news.j2").render(
        {"feed_url": x_feed_url or "", "items": items}
    )

    return template_response
