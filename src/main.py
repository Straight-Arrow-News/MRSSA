import base64
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import Response
from jinja2 import (
    Environment as JinjaEnvironment,
)
from jinja2 import (
    FileSystemLoader,
)
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.partners import flipboard as flipboard_module

from .environment import (
    GRAFANA_LABS_TOKEN,
    OTEL_DEPLOYMENT_ENVIRONMENT,
    OTEL_EXPORTER_OTLP_ENDPOINT,
)

resource = Resource(
    attributes={
        "service.name": "mrssa",
        "service.namespace": "platform",
        "deployment.environment": OTEL_DEPLOYMENT_ENVIRONMENT,
    }
)
base64_token = base64.b64encode(f"1272998:{GRAFANA_LABS_TOKEN}".encode()).decode()

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=f"{OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces",
        headers={"Authorization": f"Basic {base64_token}"},
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

log_exporter = OTLPLogExporter(
    endpoint=f"{OTEL_EXPORTER_OTLP_ENDPOINT}/v1/logs",
    headers={"Authorization": f"Basic {base64_token}"},
)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(otel_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

logging.getLogger().setLevel(logging.INFO)

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
    from src.partners import imds

    template_response = await imds.get_imds_feed(templates, x_feed_url or "")

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/middleblock", response_class=Response)
async def middleblock_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    from src.partners import middleblock

    template_response = await middleblock.get_middleblock_feed(
        templates, x_feed_url or ""
    )

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/newsbreak", response_class=Response)
async def newsbreak_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    from src.partners import newsbreak

    template_response = await newsbreak.get_newsbreak_feed(templates, x_feed_url or "")

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/simplefeed-msn", response_class=Response)
async def simplefeed_msn_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    from src.partners import simplefeed_msn

    template_response = await simplefeed_msn.get_simplefeed_msn_feed(
        templates, x_feed_url or ""
    )

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/smart-news", response_class=Response)
async def smart_news_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    from src.partners import smart_news

    template_response = await smart_news.get_smart_news_feed(
        templates, x_feed_url or ""
    )

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/wurl", response_class=Response)
async def wurl_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    from src.partners import wurl

    template_response = await wurl.get_wurl_feed(templates, x_feed_url or "")

    return Response(
        content=template_response,
        media_type="text/xml",
    )


@app.get("/yahoo_articles", response_class=Response)
async def yahoo_articles_route(
    request: Request,
    x_feed_url: feed_url_type = None,
):
    from src.partners import yahoo_articles

    template_response = await yahoo_articles.get_yahoo_articles_feed(x_feed_url or "")

    return Response(
        content=template_response,
        media_type="text/xml",
    )


FastAPIInstrumentor.instrument_app(app)
