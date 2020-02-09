#!/bin/sh
set -e
cd `dirname $0`
dst_dir="."
rsync -c -avz --delete \
    --exclude='restworld' \
    --exclude=src \
    --exclude='.??*' \
    --exclude='*'.sh \
    --exclude='?' \
    --exclude='.?' \
    --exclude='favicon.p*' \
    . kcrca_claritypack@ssh.phx.nearlyfreespeech.net:$dst_dir/
