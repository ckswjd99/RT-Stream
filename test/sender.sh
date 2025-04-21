#!/usr/bin/env bash

FFMPEG_BIN=${FFMPEG_BIN:-ffmpeg-srt}

if [ "$1" = "camera" ]; then
    SRC="-f v4l2 -r 30 -video_size 1280x720 -i /dev/video0  \
         -use_wallclock_as_timestamps 1"
else
    SRC="-re -i input.mp4 -fflags +genpts -vsync passthrough"
fi

$FFMPEG_BIN $SRC -re \
    -i input.mp4 \
    -fflags +genpts          \
    -vsync passthrough       \
    -c:v libx264 -preset veryfast -tune zerolatency \
    -g 30 -keyint_min 30 -bf 0 \
    -f mpegts \
    "srt://127.0.0.1:6000?mode=caller&pkt_size=1316&latency=20000"
