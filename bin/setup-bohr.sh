#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -z "${1-}" ]; then
    SOFTWARE_DIR="$DIR/../../bohr-software"
    echo "Path to software_path is not passed. Using the default one."
else
    SOFTWARE_DIR="$1"
fi

echo "Software needed to run bohr heuristics will be installed to $SOFTWARE_DIR"

pip install --upgrade pip setuptools wheel

BOHR_VERSION="$(bash $DIR/bohr-version.sh)"

echo "Instaling  BOHR framework version $BOHR_VERSION..."

pip install Cython==0.29.21
export SKLEARN_NO_OPENMP=1
pip install git+https://github.com/giganticode/bohr-framework@v$BOHR_VERSION

DVC_VERSION="$(curl -L https://raw.githubusercontent.com/giganticode/bohr-framework/v$BOHR_VERSION/DVC_VERSION)"
echo "Installing dvc version $DVC_VERSION..."
pip install "dvc[all]==$DVC_VERSION"
dvc config core.check_update false

bash tools/install-refactoring-miner $SOFTWARE_DIR

pip install -r requirements.txt

bohr config software_path $SOFTWARE_DIR
