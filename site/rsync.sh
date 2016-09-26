#!/bin/sh
dst_dir="site"
if [ x"$1" == x"-f" ]; then
    dst_dir="."
fi
rsync -avz --delete --delete-excluded --exclude=srcs --exclude='.??*' --exclude=rsync.sh . kcrca_claritypack@ssh.phx.nearlyfreespeech.net:$dst_dir/
