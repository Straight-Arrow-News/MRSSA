import logging

import httpx

logger = logging.getLogger(__name__)

fields = [
    "id",
    "title",
    "link",
    "bylines",
    "taxonomies",
    "date_gmt",
    "featured_image",
    "title",
    "video",
    "content.rendered"
]

PARENT_API_URL = "https://api.san.com/wp-json/wp/v2/sa_watch_listen?san_v2&_fields=parent&per_page=20"
VIDEO_API_URL = "https://api.san.com/wp-json/wp/v2/sa_core_content/?san_v2&_fields={fields}&include={include}&per_page=20"


async def fetch_videos():
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(PARENT_API_URL)
        response.raise_for_status()
        api_data = response.json()
        parent_ids = [item["parent"] for item in api_data]
        logger.debug("Fetched parent ids: %s", parent_ids)
        response = await client.get(VIDEO_API_URL.format(fields=",".join(fields), include=",".join(map(str, parent_ids))))
        # response = await client.get(VIDEO_API_URL.format(fields=",".join(fields), include="505829"))
        # 505829
        response.raise_for_status()
    return response.json()
