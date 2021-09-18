from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from labels import CommitLabel


@Heuristic(Commit)
def bugless_if_many_files_changes(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) > 15:
        return CommitLabel.NonBugFix
    else:
        return None