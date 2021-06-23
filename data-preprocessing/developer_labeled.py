#!/usr/bin/env python3

import os
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

path_to_file = os.path.realpath(__file__)
repo_root = Path(path_to_file).parent.parent

INPUT_ZIP = repo_root / "downloaded-data" / "developer-labeled-commits.zip"
SAVE_TO = repo_root / "data" / "developer-labeled.csv"

with tempfile.TemporaryDirectory() as dir:
    subprocess.run(["unzip", INPUT_ZIP, "-d", dir])

    commits = pd.read_csv(
        Path(dir) / "msr-data-master" / "Commits.csv",
        names=["id", "sha", "project", "author", "committer", "date", "message"],
    )
    # projects = pd.read_csv(DIR / 'Projects.csv', names=['id', 'date', 'url'])
    survey_results = pd.read_csv(
        Path(dir) / "msr-data-master" / "SurveyResults.csv",
        names=[
            "id",
            "sw_adaptive",
            "sw_corrective",
            "sw_perfective",
            "nfr_maintainability",
            "nfr_usability",
            "nfr_functionality",
            "nfr_reliability",
            "nfr_efficiency",
            "nfr_portability",
            "nfr_none",
            "hl_forward",
            "hl_reengineering",
            "hl_corrective",
            "hl_management",
        ],
    )

merged = pd.merge(commits, survey_results, on="id")

result = merged[["sha", "message", "sw_corrective"]]
result.columns = ["sha", "message", "bug"]

result["owner"] = ""
result["repository"] = ""

result.to_csv(SAVE_TO, index_label="commit_id")
