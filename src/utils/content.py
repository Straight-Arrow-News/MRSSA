from xml.etree import ElementTree as ET

import httpx


def prepend_video_player(html_content: str, player_url: str) -> str:
    video_header = f'<div style="position: relative; display: block; max-width: 960px;"> <div style="padding-top: 56.25%;"> <iframe src="{player_url}" allowfullscreen="" allow="encrypted-media" style="position: absolute; top: 0px; right: 0px; bottom: 0px; left: 0px; width: 100%; height: 100%;"></iframe> </div></div>'
    return video_header + html_content


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
