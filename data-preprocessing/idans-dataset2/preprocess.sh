#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

bohr_root="$1"

unzip "$bohr_root/downloaded-data/plain_commits_batch_1m_test_labels.csv.zip" -d "$bohr_root/data/bugginess/test"
rm -r "$bohr_root/data/bugginess/test/__MACOSX"

python -c "import pandas as pd; path='$bohr_root/data/bugginess/test/plain_commits_batch_1m_test_labels.csv'; df=pd.read_csv(path);df['bug']=df['is_corrective'].astype(int);df.to_csv(path)"
