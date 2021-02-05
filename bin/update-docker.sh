#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

base_ref="$1"

if [ -z "$base_ref" ]; then
    base_ref="origin/master"
fi

if [ -n "$(git --no-pager diff $base_ref -- Dockerfile)" ]; then
    docker build --tag giganticode/bohr-cml-base:latest .
    docker push giganticode/bohr-cml-base:latest
else
    echo "Dockerfile hasn't change."
fi
