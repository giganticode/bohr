from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def no_files_have_modified_status(commit: Commit) -> Optional[OneOrManyLabels]:
    if len(commit.commit_files) == 0 or commit.commit_files[0].status == "empty":
        return None
    for file in commit.commit_files:
        if file.status == "modified":
            return None
    return CommitLabel.NonBugFix

