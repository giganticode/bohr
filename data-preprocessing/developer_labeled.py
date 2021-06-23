#!/usr/bin/env python3

import os
from pathlib import Path

import pandas as pd

path_to_file = os.path.realpath(__file__)
repo_root = Path(path_to_file).parent.parent

DIR = repo_root / "downloaded-data" / "developer-labeled"
SAVE_TO = repo_root / "data" / "developer-labeled.csv"

commits = pd.read_csv(
    DIR / "Commits.csv",
    names=["id", "sha", "project", "author", "committer", "date", "message"],
)
# projects = pd.read_csv(DIR / 'Projects.csv', names=['id', 'date', 'url'])
survey_results = pd.read_csv(
    DIR / "SurveyResults.csv",
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

result.to_csv(SAVE_TO, index_label="commit_id")
