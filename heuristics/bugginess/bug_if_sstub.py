from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bug_if_sstub(commit: Commit) -> Optional[OneOrManyLabels]:
    if "mine_sstubs/head" in commit.raw_data and commit.raw_data["mine_sstubs/head"]:
        return CommitLabel.BugFix
