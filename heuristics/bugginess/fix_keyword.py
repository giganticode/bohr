from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def fix_keyword(commit: Commit) -> Optional[OneOrManyLabels]:
    """
    >>> from types import SimpleNamespace
    >>> res = fix_keyword(Commit({"message": "MaxCount not working correctly in user/group query when"}))
    >>> res is None
    True
    >>> fix_keyword(Commit({"message": "fix unit-test"}))
    CommitLabel.BugFix
    """
    if commit.message.match_ngrams(["fix"]):
        return CommitLabel.BugFix
    return None
