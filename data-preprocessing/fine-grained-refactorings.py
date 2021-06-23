#!/usr/bin/env python3

import os
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

path_to_file = os.path.realpath(__file__)
repo_root = Path(path_to_file).parent.parent

INPUT_ZIP = repo_root / "downloaded-data" / "fine-grained-refactorings.zip"
SAVE_TO = repo_root / "data" / "fine-grained-refactorings.csv"


with tempfile.TemporaryDirectory() as dir:
    subprocess.run(["unzip", INPUT_ZIP, "-d", dir])
    dfs = [
        pd.read_csv(file)
        for file in (Path(dir) / "manualy_labeled_commits (goldset)").iterdir()
    ]
    concat_dfs = pd.concat(dfs, axis=0, ignore_index=True)
    concat_dfs["owner"] = ""
    concat_dfs["repository"] = ""
    new_columns = concat_dfs.columns.values.tolist()
    new_columns[0] = "sha"
    concat_dfs.columns = new_columns
    concat_dfs.to_csv(SAVE_TO, index_label="commit_id")


# echo "sha,commit_date,message,refactoring_class,refactoring_type,owner,repository" >> "$OUTPUT_CSV"
