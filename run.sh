#!/bin/bash
cd /opt/hopehub/media_downloader_service
git pull
pip3 install -r requirements.txt
pkill -f "5003"
nohup gunicorn -w 2 -b 0.0.0.0:5003 app:app > log.txt 2>&1 &