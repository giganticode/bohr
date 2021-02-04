#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

tools_dir="$1"

if [ -z "$tools_dir" ]; then
    echo "Path to the tools dir should be passed"
    exit 2
fi

if ! command -v unzip &> /dev/null
then
    echo "unzip could not be found. Trying to install it ..."
    apt-get update && apt-get install -y unzip
fi

if ! [ -d tools_dir ]; then
    mkdir "$tools_dir"
fi
cd "$tools_dir"
git clone https://github.com/tsantalis/RefactoringMiner
cd RefactoringMiner
./gradlew distZip
ZIP_NAME="$(ls build/distributions)"
cd ..
unzip "RefactoringMiner/build/distributions/$ZIP_NAME"
ls
rm -rf "RefactoringMiner"