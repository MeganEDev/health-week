#!/bin/sh
# Rebuild and serve on localhost so the laptop matches what the phone gets.
set -e
cd "$(dirname "$0")"
python3 build.py
PORT=${PORT:-8000}
echo "serving http://localhost:$PORT  —  ctrl-c to stop"
( sleep 1; open "http://localhost:$PORT" ) &
exec python3 -m http.server "$PORT" --directory docs
