from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bugless_if_one_removed_file(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) == 1 and commit.commit_files[0].status == "removed":
        return CommitLabel.NonBugFix
    return None
