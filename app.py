from flask import Flask, request, jsonify
from downloader import download_from_url

app = Flask(__name__)

@app.route("/api/media-download", methods=["GET"])
def api_download():
    url = request.args.get("url", "")
    if not url:
        return jsonify({'status': 'error', 'message': 'Missing URL'}), 400
    result = download_from_url(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
