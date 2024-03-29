from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bugless_if_many_files_changes(commit: Commit) -> Optional[OneOrManyLabels]:
    if len(commit.commit_files) > 15:
        return CommitLabel.NonBugFix
    else:
        return None
