from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def commit_explorer_output_sstubs(commit: Commit) -> Optional[Labels]:
    if "mine_sstubs/head" in commit.raw_data and commit.raw_data["mine_sstubs/head"]:
        return CommitLabel.BugFix
