from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from labels import CommitLabel


@Heuristic(Commit)
def bugless_if_at_least_5_added_files(commit: Commit) -> Optional[Labels]:
    added_count = 0
    for file in commit.commit_files:
        if file.status == "added":
            added_count += 1
    return CommitLabel.NonBugFix if added_count >= 5 else None