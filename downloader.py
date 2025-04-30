
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import os
import requests

# URL cookies từ R2
COOKIE_URL_MAP = {
    "x.com": "https://r2.lam.io.vn/cookies/x_cookies.txt",
    "twitter.com": "https://r2.lam.io.vn/cookies/x_cookies.txt",
    "instagram.com": "https://r2.lam.io.vn/cookies/instagram_cookies.txt",
    "facebook.com": "https://r2.lam.io.vn/cookies/facebook_cookies.txt",
    "tiktok.com": "https://r2.lam.io.vn/cookies/tiktok_cookies.txt",
}

def download_from_url(url):
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        cookiefile = None
        if domain in COOKIE_URL_MAP:
            cookiefile = f"/tmp/{domain.replace('.', '_')}_cookies.txt"
            r = requests.get(COOKIE_URL_MAP[domain], timeout=10)
            with open(cookiefile, "wb") as f:
                f.write(r.content)

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "force_generic_extractor": False,
        }
        if cookiefile:
            ydl_opts["cookiefile"] = cookiefile

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            media_list = []
            if "entries" in info:
                media_list = [_extract_item(entry) for entry in info["entries"] if _extract_item(entry)]
            else:
                item = _extract_item(info)
                if item:
                    media_list.append(item)
            if not media_list:
                return {'status': 'error', 'message': 'No media could be extracted from this URL.'}
            return {'status': 'ok', 'media': media_list}

    except Exception as e:
        if "twitter" in url or "x.com" in url:
            return {'status': 'error', 'message': 'Twitter/X media could not be parsed. It may require login, or yt-dlp update. Check cookie and try again.'}
        return {'status': 'error', 'message': str(e)}

def _extract_item(info):
    try:
        formats = info.get("formats", [])
        best = max(formats, key=lambda f: f.get("height", 0)) if formats else None
        media_url = best.get("url") if best else info.get("url")
        if not media_url:
            return None
        return {
            "title": info.get("title"),
            "url": media_url,
            "thumbnail": info.get("thumbnail"),
            "ext": best.get("ext") if best else info.get("ext", "mp4"),
            "webpage_url": info.get("webpage_url"),
        }
    except:
        return None
