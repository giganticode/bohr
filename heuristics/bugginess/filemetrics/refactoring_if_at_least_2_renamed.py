from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def refactoring_if_at_least_2_renamed(commit: Commit) -> Optional[OneOrManyLabels]:
    renamed_count = 0
    for file in commit.commit_files:
        if file.status == "renamed":
            renamed_count += 1
    return CommitLabel.Refactoring if renamed_count >= 2 else None
