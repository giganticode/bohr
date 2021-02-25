#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

pip install jq===1.1.2 -qqq

BOHR_VERSION=$(python -c "\
import jq; \
bohr_config = open(\"$(pwd)/bohr.json\").read(); \
print(jq.compile('.bohr_framework_version').input(text=bohr_config).first())")

echo "$BOHR_VERSION"