from typing import Dict, List, Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Dataset, Experiment, Task, Workspace
from bohrlabels.labels import CommitLabel


def id_with_files(id: str, conditions: Optional[List[Dict]] = None) -> Dict:
    return {
        "$and": [
            {id: {"$exists": True}},
            {"files": {"$exists": True}},
            {"files": {"$type": "array"}},
        ]
        + (conditions if conditions is not None else [])
    }


commits_200k_files = Dataset(
    id="commits_200k_files",
    top_artifact=Commit,
    query=id_with_files("bohr.200k_commits"),
)

berger_files = Dataset(
    id="berger_files", top_artifact=Commit, query=id_with_files("manual_labels.berger")
)
levin_files = Dataset(
    id="levin_files", top_artifact=Commit, query=id_with_files("manual_labels.levin")
)
herzig = Dataset(id="manual_labels.herzig", top_artifact=Commit)
mauczka_files = Dataset(
    id="mauczka_files",
    top_artifact=Commit,
    query=id_with_files("manual_labels.mauczka"),
)
idan_files = Dataset(
    id="idan_files",
    top_artifact=Commit,
    query=id_with_files("idan/0_1", [{"idan/0_1.Is_Corrective": {"$exists": True}}]),
)


bugginess = Task(
    name="bugginess",
    author="hlib",
    description="bug or not",
    top_artifact=Commit,
    labels=[CommitLabel.NonBugFix, CommitLabel.BugFix],
    test_datasets={
        idan_files: lambda c: (
            CommitLabel.BugFix
            if c.raw_data["idan/0_1"]["Is_Corrective"]
            else CommitLabel.NonBugFix
        ),
        levin_files: lambda c: (
            CommitLabel.BugFix
            if c.raw_data["manual_labels"]["levin"]["bug"] == 1
            else CommitLabel.NonBugFix
        ),
        berger_files: lambda c: (
            CommitLabel.BugFix
            if c.raw_data["manual_labels"]["berger"]["bug"] == 1
            else CommitLabel.NonBugFix
        ),
        herzig: lambda c: (
            CommitLabel.BugFix
            if c.raw_data["manual_labels"]["herzig"]["CLASSIFIED"] == "BUG"
            else CommitLabel.NonBugFix
        ),
        mauczka_files: lambda c: (
            CommitLabel.BugFix
            if c.raw_data["manual_labels"]["mauczka"]["hl_corrective"] == 1
            else CommitLabel.NonBugFix
        ),
    },
)

default_exp = Experiment(
    "bugginess_default_exp",
    bugginess,
    train_dataset=commits_200k_files,
    heuristics_classifier="bugginess@0a56f59c95ca87ee324c365bf2eb71b212a6045e",
)
