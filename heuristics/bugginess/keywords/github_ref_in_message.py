import re
from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels

GITHUB_REF_RE = re.compile(r"gh(-|\s)\d+", flags=re.I)


@Heuristic(Commit)
def github_ref_in_message(commit: Commit) -> Optional[Labels]:
    """
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "gh-123: bug"))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "gh 123"))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "GH 123: bug2"))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "GH123: wrong issue reference")) is None
    True
    """
    return l.CommitLabel.BugFix if GITHUB_REF_RE.search(commit.message.raw) else None
