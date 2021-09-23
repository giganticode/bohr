from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def bugless_if_one_added_file(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) == 1 and commit.commit_files[0].status == "added":
        return CommitLabel.NonBugFix
    return None
