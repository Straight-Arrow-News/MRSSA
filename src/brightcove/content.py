from httpx import AsyncClient


async def get_video_info(
    video_id: str, account_id: str, policy_key: str
) -> dict[str, str]:
    url = f"https://edge.api.brightcove.com/playback/v1/accounts/{account_id}/videos/{video_id}"
    headers = {"bcov-policy": policy_key}

    async with AsyncClient(timeout=60.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        video = response.json()

        mp4_source = next(
            (s for s in video.get("sources", []) if s.get("container") == "MP4"), None
        )

        if not mp4_source:
            raise RuntimeError("mp4_source not found")

        return {
            "duration": str(mp4_source.get("duration")),
            "bitrate": str(mp4_source.get("avg_bitrate")),
            "content_url": mp4_source.get("src"),
        }

def prepend_video_player(html_content: str, player_url: str) -> str:
    video_header = f'<div style="position: relative; display: block; max-width: 960px;"> <div style="padding-top: 56.25%;"> <iframe src="{player_url}" allowfullscreen="" allow="encrypted-media" style="position: absolute; top: 0px; right: 0px; bottom: 0px; left: 0px; width: 100%; height: 100%;"></iframe> </div></div>'
    return video_header + html_content
