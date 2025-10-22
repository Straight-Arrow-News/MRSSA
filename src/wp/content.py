from datetime import datetime

from bs4 import BeautifulSoup

remove_divs = [
    "wp-block-san-app-download",
    "wp-block-san-san-inarticle-newsletter-signup",
    "wp-block-san-san-inarticle-social-share",
]

def parse_content(content: str) -> str:
    post_data = BeautifulSoup(
        content,
        "html.parser"
    )

    for div_class in remove_divs:
        div_block = post_data.find("div", class_=div_class)
        if div_block:
            div_block.decompose()

    return str(post_data).replace('\n', '').replace('\r', '')

def format_date(date_published: str) -> tuple[str, str]:
    pubdate_formatted = ""
    valid_start = ""
    if date_published:
        dt = datetime.fromisoformat(date_published)
        dt_utc = dt.replace(tzinfo=None)
        pubdate_formatted = dt_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
        valid_start = dt_utc.isoformat() + "Z"
    return pubdate_formatted, valid_start
