from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def buggless_one_file(commit: Commit) -> Optional[OneOrManyLabels]:
    return CommitLabel.NonBugFix if len(commit.commit_files) == 1 else None
