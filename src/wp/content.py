from datetime import datetime

from bs4 import BeautifulSoup

remove_divs = [
    "wp-block-san-app-download",
    "wp-block-san-san-inarticle-newsletter-signup",
    "wp-block-san-san-inarticle-social-share",
]

twitter_embed = """
    <blockquote class="twitter-tweet">
        <a href="{link}"></a>
    </blockquote>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
"""

append = """
<p>The post <a href="{link}">{title}</a> appeared first on <a href="https://san.com">Straight Arrow News</a>.</p>
"""

def parse_content(content: str, link: str, title: str) -> str:
    post_data = BeautifulSoup(
        content,
        "html.parser"
    )

    for tweet in post_data.css.select(".wp-block-embed__wrapper"):
        tweet.replace_with(
            BeautifulSoup(
                twitter_embed.format(link=tweet.text),
                "html.parser"
            )
        )

    post_data = str(post_data) + append.format(link=link, title=title)
    return post_data.replace('\n', '').replace('\r', '')

def format_date(date_published: str) -> tuple[str, str]:
    pubdate_formatted = ""
    valid_start = ""
    if date_published:
        dt = datetime.fromisoformat(date_published)
        dt_utc = dt.replace(tzinfo=None)
        pubdate_formatted = dt_utc.strftime("%a, %d %b %Y %H:%M:%S GMT")
        valid_start = dt_utc.isoformat() + "Z"
    return pubdate_formatted, valid_start
