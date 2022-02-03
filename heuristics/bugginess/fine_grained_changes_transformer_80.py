from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel

label_map = {
    "build": CommitLabel.NonBugFix,
    "chore": CommitLabel.NonBugFix,
    "ci": CommitLabel.NonBugFix,
    "docs": CommitLabel.NonBugFix,
    "feat": CommitLabel.Feature,
    "fix": CommitLabel.BugFix,
    "perf": CommitLabel.NonBugFix,
    "refactor": CommitLabel.Refactoring,
    "style": CommitLabel.NonBugFix,
    "test": CommitLabel.NonBugFix
}


@Heuristic(Commit)
def fine_grained_changes_transformer_80(commit: Commit) -> Optional[Labels]:
    if "bohr" in commit.raw_data and "change_transformer_label/0_1" in commit.raw_data["bohr"]:
        val = float(commit.raw_data["bohr"]["change_transformer_label/0_1"]['probability'])
        if 0.8 < val <= 0.9:
            return label_map[commit.raw_data["bohr"]["change_transformer_label/0_1"]['label']]