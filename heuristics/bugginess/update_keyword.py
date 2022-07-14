from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def update_keyword(commit: Commit) -> Optional[OneOrManyLabels]:
    """
    >>> from types import SimpleNamespace
    >>> res = update_keyword(Commit({"message": "MaxCount not working correctly in user/group query when"}))
    >>> res is None
    True
    >>> update_keyword(Commit({"message": "update unit-test"}))
    CommitLabel.NonBugFix
    """
    if commit.message.match_ngrams(["updat"]):
        return CommitLabel.NonBugFix
    return None
