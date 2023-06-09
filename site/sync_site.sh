#!/bin/sh
set -e
cd `dirname $0`
dst_dir="."
rsync -c -avz --delete --progress \
    --exclude='restworld' \
    --exclude='philter' \
    --exclude=src \
    --exclude='.??*' \
    --exclude='*'.sh \
    --exclude='?' \
    --exclude='.?' \
    --exclude='favicon.p*' \
    --exclude='*.bak' \
    . kcrca_claritypack@ssh.phx.nearlyfreespeech.net:$dst_dir/
