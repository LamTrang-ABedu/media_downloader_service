import os
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import requests

COOKIE_MAP = {
    "x.com": "https://r2.lam.io.vn/cookies/x_cookies.txt",
    "twitter.com": "https://r2.lam.io.vn/cookies/x_cookies.txt",
    "instagram.com": "https://r2.lam.io.vn/cookies/instagram_cookies.txt",
    "facebook.com": "https://r2.lam.io.vn/cookies/facebook_cookies.txt",
    "tiktok.com": "https://r2.lam.io.vn/cookies/tiktok_cookies.txt",
}

def download_from_url(url):
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        if domain in COOKIE_MAP:
            cookiefile = f"/tmp/{domain.replace('.', '_')}_cookies.txt"
            r = requests.get(COOKIE_MAP[domain], timeout=10)
            with open(cookiefile, "wb") as f:
                f.write(r.content)
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'force_generic_extractor': False,
        }
        if cookiefile:
            ydl_opts["cookiefile"] = cookiefile

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            media_list = []
            if 'entries' in info:
                for entry in info['entries']:
                    media_list.append(_extract_item(entry))
            else:
                media_list.append(_extract_item(info))
        return {'status': 'ok', 'media': media_list}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def _extract_item(info):
    return {
        'title': info.get('title'),
        'url': info.get('url'),
        'thumbnail': info.get('thumbnail'),
        'ext': info.get('ext'),
        'webpage_url': info.get('webpage_url')
    }
