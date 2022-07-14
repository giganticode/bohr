from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def add_keyword(commit: Commit) -> Optional[OneOrManyLabels]:
    """
    >>> res = add_keyword(Commit({"message": "MaxCount not working correctly in user/group query when"}))
    >>> res is None
    True
    >>> add_keyword(Commit({"message": "add unit-test"}))
    CommitLabel.NonBugFix
    """
    if commit.message.match_ngrams(["add"]):
        return CommitLabel.NonBugFix
    return None
