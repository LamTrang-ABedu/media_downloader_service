from yt_dlp import YoutubeDL
import requests
import os

def download_from_url(url):
    try:
        ydl_opts = {
            'quiet': True,
            'force_generic_extractor': False,
        }

        # Twitter/X
        if 'x.com' in url or 'twitter.com' in url:
            cookie_path = '/tmp/x_cookies.txt'
            _download_cookie_once(
                'https://r2.lam.io.vn/cookies/x_cookies.txt',
                cookie_path
            )
            ydl_opts.update({
                'cookiefile': cookie_path,
                'skip_download': True
            })

        # Instagram
        elif 'instagram.com' in url:
            cookie_path = '/tmp/instagram_cookies.txt'
            _download_cookie_once(
                'https://r2.lam.io.vn/cookies/instagram_cookies.txt',
                cookie_path
            )
            ydl_opts.update({
                'cookiefile': cookie_path,
                'format': 'mp4',  # không merge audio, lấy link trực tiếp
                'extract_flat': False,
                'skip_download': True
            })

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

def _download_cookie_once(remote_url, local_path):
    if not os.path.exists(local_path):
        resp = requests.get(remote_url)
        if resp.ok:
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(resp.text)

def _extract_item(info):
    source_url = info.get('webpage_url', '')
    ext = info.get('ext')

    # Twitter/X
    if 'x.com' in source_url or 'twitter.com' in source_url:
        best_format = None
        if 'formats' in info:
            formats = [f for f in info['formats'] if f.get('ext') == 'mp4' and f.get('url')]
            best_format = formats[-1] if formats else None

        return {
            'title': info.get('title'),
            'url': best_format.get('url') if best_format else info.get('url'),
            'thumbnail': info.get('thumbnail'),
            'ext': best_format.get('ext') if best_format else ext,
            'webpage_url': source_url
        }

    # Instagram
    elif 'instagram.com' in source_url:
        # Nếu là ảnh
        if info.get('url', '').endswith(('.jpg', '.jpeg', '.png')):
            return {
                'title': info.get('title') or 'Instagram Image',
                'url': info.get('url'),
                'thumbnail': info.get('url'),
                'ext': 'jpg',
                'webpage_url': source_url
            }
        # Nếu là video
        elif info.get('ext') == 'mp4':
            return {
                'title': info.get('title') or 'Instagram Video',
                'url': info.get('url'),
                'thumbnail': info.get('thumbnail'),
                'ext': 'mp4',
                'webpage_url': source_url
            }

    # Default fallback
    return {
        'title': info.get('title'),
        'url': info.get('url'),
        'thumbnail': info.get('thumbnail'),
        'ext': ext,
        'webpage_url': source_url
    }