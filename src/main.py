from datetime import datetime
from typing import Annotated
from xml.etree import ElementTree as ET

import httpx
from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from jinja2 import (
    Environment as JinjaEnvironment,
)
from jinja2 import (
    FileSystemLoader,
)

app = FastAPI()


def get_mrss_template() -> JinjaEnvironment:
    return JinjaEnvironment(loader=FileSystemLoader("templates"))


feed_url_type = Annotated[
    str | None,
    Header(
        description="Used to mark which url the feed is supposed to implant in the template, useful with multiple providers require the same feed",
    ),
]


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

        link = entry.get("link", "").replace("straightarrownews.com", "san.com")

        print(f"Processing video_id: {video_id}, link: {link}")

        post_data = await fetch_post_content(link, client)

        print(
            f"Post data html length: {len(post_data['html'])}, author: {post_data['author']}"
        )

        if not link or not post_data["html"]:
            print(f"Skipping - link: {bool(link)}, html: {bool(post_data['html'])}")
            continue

        bylines = entry.get("bylines", [])
        author = bylines[0].get("name") if bylines else post_data.get("author", "")

        video_data = entry.get("video", {})
        video_description = video_data.get("description", "")

        taxonomies = entry.get("taxonomies", {})
        keywords_list = []
        for tax_key in [
            "sa_type",
            "sa_vertical",
            "sa_issue",
            "sa_topic_term",
            "sa_distro",
        ]:
            tax = taxonomies.get(tax_key, {})
            terms = tax.get("terms", [])
            for term in terms:
                keywords_list.append(term.get("slug", ""))
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
        title = title_data.get("rendered", "") if isinstance(title_data, dict) else ""

        player_url = f"https://players.brightcove.net/6279053007001/Jkljh8LEJ_default/index.html?videoId={video_id}"

        guid = f"6279053007001:{video_id}"

        item = {
            "title": title,
            "guid": guid,
            "link": link,
            "pubdate": pubdate_formatted,
            "description": video_description or title,
            "author": author,
            "content": post_data["html"],
            "valid_start": valid_start,
            "thumbnail_url": thumbnail_url,
            "player_url": player_url,
            "keywords": keywords_str,
        }
        items.append(item)

    return items


@app.get("/flipboard", response_class=Response)
async def flipboard(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = "",
):
    api_url = "https://api.san.com/wp-json/wp/v2/sa_core_content/?san_v2&per_page=20"

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        items = await transform_api_data_to_feed_items(api_data, client)

    template_response = templates.get_template("flipboard.j2").render(
        {"feed_url": x_feed_url, "items": items}
    )

    return Response(
        content=template_response,
        media_type="text/xml",
    )
