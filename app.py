from flask import Flask, request, jsonify, Response
from downloader import download_from_url
import requests

app = Flask(__name__)

@app.route("/api/proxy")
def proxy():
    real_url = request.args.get("real_url")
    ua = request.args.get("ua", "Mozilla/5.0")
    referer = request.args.get("referer", None)

    headers = {"User-Agent": ua}
    if referer:
        headers["Referer"] = referer

    r = requests.get(real_url, headers=headers, stream=True)
    return Response(r.iter_content(chunk_size=8192), content_type=r.headers.get("Content-Type"))

@app.route("/api/media-download", methods=["GET"])
def api_download():
    url = request.args.get("url", "")
    if not url:
        return jsonify({'status': 'error', 'message': 'Missing URL'}), 400
    result = download_from_url(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
