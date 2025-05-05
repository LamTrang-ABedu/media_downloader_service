from yt_dlp import YoutubeDL
import requests
import os
from urllib.parse import urlparse

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
            print(f"Downloading cookies for {domain}...")
            cookiefile = f"/tmp/{domain.replace('.', '_')}_cookies.txt"

            # Tải cookie và xử lý lỗi
            if not _download_cookie_once(COOKIE_URL_MAP[domain], cookiefile):
                return {'status': 'error', 'message': f"Failed to download cookies for {domain}"}

        ydl_opts = {
            "quiet": True,
            "force_generic_extractor": False,
        }
        if domain == 'tiktok.com':
            ydl_opts.update({
                'cookiefile': cookiefile,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
                    'Referer': 'https://www.tiktok.com/',
                    'Origin': 'https://www.tiktok.com',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
            })

        elif domain == 'youtube.com':
            ydl_opts.update({
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            })

        elif domain == 'x.com' or domain == 'twitter.com' or domain == 'instagram.com' or domain == 'facebook.com':
            ydl_opts.update({
                'cookiefile': cookiefile,
                'skip_download': True
            })


        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return {'status': 'error', 'message': 'Failed to extract media info'}

            media_list = []
            if 'entries' in info:
                for entry in info['entries']:
                    media_list.append(_extract_item(entry))
            else:
                media_list.append(_extract_item(info))

        return {'status': 'ok', 'media': media_list}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def _download_cookie_once(remote_url, local_path):
    try:
        if not os.path.exists(local_path):
            resp = requests.get(remote_url)
            if resp.ok:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                return True
            else:
                print(f"Failed to download cookies from {remote_url}: {resp.status_code}")
                return False
        return True
    except Exception as e:
        print(f"Error downloading cookies: {str(e)}")
        return False

def _extract_item(info):
    source_url = info.get('webpage_url', '')
    ext = info.get('ext')
    url = info.get('url')

    # ✅ Fallback: nếu url bị null thì lấy từ formats
    if not url and 'formats' in info:
        formats = [f for f in info['formats'] if f.get('url')]
        if formats:
            best = formats[-1]
            url = best.get('url')
            ext = best.get('ext', ext)

    # 🐦 Twitter/X
    if 'x.com' in source_url or 'twitter.com' in source_url:
        best_format = None
        if 'formats' in info:
            formats = [f for f in info['formats'] if f.get('ext') == 'mp4' and f.get('url')]
            best_format = formats[-1] if formats else None

        return {
            'title': info.get('title'),
            'url': best_format.get('url') if best_format else url,
            'thumbnail': info.get('thumbnail'),
            'ext': best_format.get('ext') if best_format else ext,
            'webpage_url': source_url
        }

    # 📸 Instagram
    elif 'instagram.com' in source_url:
        # Nếu là ảnh
        if url and url.endswith(('.jpg', '.jpeg', '.png')):
            return {
                'title': info.get('title') or 'Instagram Image',
                'url': url,
                'thumbnail': url,
                'ext': 'jpg',
                'webpage_url': source_url
            }
        # Nếu là video
        elif ext == 'mp4':
            return {
                'title': info.get('title') or 'Instagram Video',
                'url': url,
                'thumbnail': info.get('thumbnail'),
                'ext': 'mp4',
                'webpage_url': source_url
            }

    # 🌐 Mặc định (Facebook, TikTok, YouTube...)
    return {
        'title': info.get('title'),
        'url': url,
        'thumbnail': info.get('thumbnail'),
        'ext': ext,
        'webpage_url': source_url
    }
