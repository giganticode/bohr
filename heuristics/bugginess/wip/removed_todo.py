from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from labels import CommitLabel


@Heuristic(Commit)
def removed_todo(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        for change in file.parsed_changes:
            if change[0] == "del" and "TODO" in change[1]:
                return (
                    CommitLabel.Refactoring
                )  # TODO not sure about this one, what about XXX?
    return None
