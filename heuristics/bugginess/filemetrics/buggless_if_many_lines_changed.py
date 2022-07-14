from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def buggless_if_many_lines_changed(commit: Commit) -> Optional[OneOrManyLabels]:
    sum = 0
    for file in commit.commit_files:
        if file.changes:
            sum += len(file.changes)
    return CommitLabel.NonBugFix if sum > 16000 else None