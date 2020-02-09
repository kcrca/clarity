#!/bin/sh
set -e
cd `dirname $0`
dst_dir="."
rsync -c -avz --delete --delete-excluded --exclude=src --exclude='.??*' --exclude='*'.sh --exclude='?' --exclude='.?' . kcrca_claritypack@ssh.phx.nearlyfreespeech.net:$dst_dir/
