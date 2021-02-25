#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SOFTWARE_DIR="$1"

if [ -z "$SOFTWARE_DIR" ]; then
    echo "Path to the tools dir should be passed"
    exit 2
fi

pip install --upgrade pip setuptools wheel

pip install jq==1.1.2

BOHR_VERSION=$(python -c "\
import jq; \
bohr_config = open(\"$(pwd)/bohr.json\").read(); \
print(jq.compile('.bohr_framework_version').input(text=bohr_config).first())")

echo "Instaling  BOHR framework version $BOHR_VERSION..."

pip install Cython==0.29.21
export SKLEARN_NO_OPENMP=1
pip install git+https://github.com/giganticode/bohr-framework@$BOHR_VERSION

bash tools/install-refactoring-miner $SOFTWARE_DIR

pip install -r requirements.txt