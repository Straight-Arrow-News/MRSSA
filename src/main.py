from typing import Annotated

from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import Response
from jinja2 import (
    Environment as JinjaEnvironment,
)
from jinja2 import (
    FileSystemLoader,
)

from src.partners import flipboard as flipboard_module
from src.partners import imds

app = FastAPI()


def get_mrss_template() -> JinjaEnvironment:
    return JinjaEnvironment(loader=FileSystemLoader("templates"))


feed_url_type = Annotated[
    str | None,
    Header(
        description="Used to mark which url the feed is supposed to implant in the template, useful with multiple providers require the same feed",
    ),
]


@app.get("/flipboard", response_class=Response)
async def flipboard(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    template_response = await flipboard_module.get_flipboard_feed(
        templates, x_feed_url or ""
    )

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/imds", response_class=Response)
async def imds_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    template_response = await imds.get_imds_feed(templates, x_feed_url or "")

    return Response(
        content=template_response,
        media_type="text/xml",
    )
