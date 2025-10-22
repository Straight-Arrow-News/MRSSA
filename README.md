# MRSS feed generator for SAN syndication partners
This will generate mrss feeds (xml) for our synidation partners

# Prequisites
- [uv](https://github.com/astral-sh/uv)
- [make](https://formulae.brew.sh/formula/make)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/)
- [direnv](https://direnv.net/)

# Getting Started

First, run uv sync to get all dependencies installed an a virtual env created.

```bash
uv sync
```

Move `.envrc.template` to `.envrc` and fill out all of the variables. Ask someone in the [#team-platform](https://straight-arrow-news.slack.com/archives/C08BUU6TCG5) channel for these values. After these values are added to `.envrc` run:
```bash
direnv allow
```

To run it locally, start it under the virtual environment using UV:
```bash
source .venv/bin/activate
make dev
```

# Linting
To lint your code before commiting, run
```bash
make check
```

This will run the `uv ruff` command to lint your code. If you have any issues, fix them manually or yeet it by running:
```bash
uv run ruff check --fix src/
```

# Adding syndication routes
For most routes that are pulling videos only, you can add a new route to `./src/main.py` and a new template under `./templates`. Or you can reuse a template if you like.

For example:
```python
@app.get("/new-partner", response_class=Response)
async def simplefeed_msn_route(
    request: Request,
    templates: Annotated[JinjaEnvironment, Depends(get_mrss_template)],
    x_feed_url: feed_url_type = None,
):
    template_name = f"new-partner.j2" # template created for this partner, or an existing template
    feed_url = x_feed_url or request.url
    options = {
        "use_video_source": True, # Pull video source from Brightcove. If False, will just use the player url
        "player_id": "<get_new_player_id_from_bd>", # Player id from Brightcove, e.g. 8Qp6u0bJE_default

    }
    items = await build_model(options)
    template_response = templates.get_template(template_name).render(
        {"feed_url": feed_url, "items": items}
    )
    return Response(
        content=template_response,
        media_type="text/xml",
    )
```
