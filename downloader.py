from yt_dlp import YoutubeDL
import requests
import os
from urllib.parse import urlparse
from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.extractor import gen_extractor_classes
from yt_dlp import YoutubeDL

def resolve_redirect(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except:
        return url  # fallback nếu lỗi

# Patch để ép client=web cho riêng YouTube
class PatchedYoutubeIE(YoutubeIE):
    def _real_initialize(self):
        super()._real_initialize()
        self._player_client = 'web'  # Ép client thành "web" thật sự
        
# URL cookies từ R2
COOKIE_URL_MAP = {
    "x.com": "https://r2.lam.io.vn/cookies/x_cookies.txt",
    "twitter.com": "https://r2.lam.io.vn/cookies/x_cookies.txt",
    "instagram.com": "https://r2.lam.io.vn/cookies/instagram_cookies.txt",
    "facebook.com": "https://r2.lam.io.vn/cookies/facebook_cookies.txt",
    "tiktok.com": "https://r2.lam.io.vn/cookies/tiktok_cookies.txt",
    "pornhub.com": "https://r2.lam.io.vn/cookies/pornhub_cookies.txt",
    #"youtube.com": "https://r2.lam.io.vn/cookies/youtube_cookies.txt",
    #"youtu.be": "https://r2.lam.io.vn/cookies/youtube_cookies.txt",
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

        # Patch YouTube extractor nếu là YouTube
        if domain in ['youtube.com', 'youtu.be']:
            ydl_opts = {
                # 'cookiefile': cookiefile,
                'quiet': False,
                'verbose': True,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'format': 'bv+ba/best',
                'merge_output_format': 'mp4',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                'extractor_classes': [
                    PatchedYoutubeIE if e.IE_NAME == 'youtube' else e
                    for e in gen_extractor_classes()
                ]
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                media_list = []
                if 'entries' in info:
                    for entry in info['entries']:
                        media_list.append(_extract_item(entry))
                else:
                    media_list.append(_extract_item(info))

            return {'status': 'ok', 'media': media_list}
            
        ydl_opts = {
            "quiet": True,
            "force_generic_extractor": False,
            'merge_output_format': 'mp4',  # ensure video+audio merged
            'format': 'bv+ba/best',  # best video + audio or fallback
        }

        if domain == 'tiktok.com':
            print(f"[Tiktok] ydl_opts.update for {domain}...")
            # Resolve redirect
            url = resolve_redirect(url)
            print(f"[Tiktok] resolve redirect: {url}")
            ydl_opts.update({
                'cookiefile': cookiefile,
                'quiet': False,
                'verbose': True,
                'format': 'bv+ba/best',
                'merge_output_format': 'mp4',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                    'Referer': 'https://www.tiktok.com/',
                    'Origin': 'https://www.tiktok.com',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
            })
        
        elif domain in COOKIE_URL_MAP:
            ydl_opts.update({
                'cookiefile': cookiefile
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
    formats = info.get('formats', [])

    # Lọc video có height rõ ràng
    video_streams = sorted(
        [f for f in formats if f.get('vcodec') != 'none' and f.get('url') and f.get('height') is not None],
        key=lambda x: x['height'],
        reverse=True
    )

    # Nếu không có height, fallback mềm
    if not video_streams:
        video_streams = [f for f in formats if f.get('vcodec') != 'none' and f.get('url')]

    # Lọc audio có abr rõ ràng
    audio_streams = sorted(
        [f for f in formats if f.get('acodec') != 'none' and f.get('url') and f.get('abr') is not None],
        key=lambda x: x['abr'],
        reverse=True
    )

    if not audio_streams:
        audio_streams = [f for f in formats if f.get('acodec') != 'none' and f.get('url')]

    best_video = video_streams[0] if video_streams else None
    best_audio = audio_streams[0] if audio_streams else None

    if best_video and best_audio:
        return {
            'title': info.get('title'),
            'video_url': best_video.get('url'),
            'audio_url': best_audio.get('url'),
            'thumbnail': info.get('thumbnail'),
            'ext': best_video.get('ext'),
            'webpage_url': source_url,
            'needs_merge': True
        }

    # fallback cuối nếu không tách được stream
    return {
        'title': info.get('title'),
        'video_url': info.get('url'),
        'thumbnail': info.get('thumbnail'),
        'ext': info.get('ext'),
        'webpage_url': source_url,
        'needs_merge': False
    }
