from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bugless_if_at_least_2_removed_files(commit: Commit) -> Optional[OneOrManyLabels]:
    removed_count = 0
    for file in commit.commit_files:
        if file.status == "removed":
            removed_count += 1
    return CommitLabel.NonBugFix if removed_count >= 2 else None
