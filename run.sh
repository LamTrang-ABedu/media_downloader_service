#!/bin/bash
cd /opt/hopehub/media_downloader_service
git pull
pip3 install -r requirements.txt
# Chạy Flask app
/usr/bin/python3 app.py
