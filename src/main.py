from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

app = FastAPI()


def get_mrss_template() -> Jinja2Templates:
    return Jinja2Templates(directory="templates")


feed_url_type = Annotated[
    str,
    Header(
        description="Used to mark which url the feed is supposed to implant in the template, useful with multiple providers require the same feed",
    ),
]


@app.get("/")
async def root(x_feed_url: feed_url_type = None):
    return {"message": "Hello World"}


@app.get("/flipboard", response_class=Response)
async def flipboard(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    items = [
        {
            "title": "Manchester synagogue attack: car-ramming and stabbing leaves 2 dead",
            "guid": "6279053007001:6380739369112",
            "link": "https://san.com/cc/manchester-synagogue-attack-car-ramming-and-stabbing-leaves-2-dead/",
            "pubdate": "Thu, 02 Oct 2025 16:03:08 GMT",
            "description": "Police say a car-ramming and stabbing attack outside Manchester in the United Kingdom has killed at least two people.",
            "author": "Craig Nigrelli",
            "content": "<p>Sample content here...</p>",
            "valid_start": "2025-10-02T16:03:08.491Z",
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "player_url": "https://players.brightcove.net/6279053007001/Jkljh8LEJ_default/index.html?videoId=6380739369112",
            "keywords": "update,manchester,terrorism",
        }
    ]

    template_response = templates.TemplateResponse(
        "flipboard.j2", {"request": request, "feed_url": x_feed_url, "items": items}
    )

    return Response(
        content=template_response.body,
    )
