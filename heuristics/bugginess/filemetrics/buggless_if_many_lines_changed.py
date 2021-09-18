from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from labels import CommitLabel


@Heuristic(Commit)
def buggless_if_many_lines_changed(commit: Commit) -> Optional[Labels]:
    sum = 0
    for file in commit.commit_files:
        if file.changes:
            sum += len(file.changes)
    return CommitLabel.NonBugFix if sum > 5000 else None