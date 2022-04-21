import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel

GITHUB_REF_RE = re.compile(r"gh(-|\s)\d+", flags=re.I)


@Heuristic(Commit)
def github_ref_in_message(commit: Commit) -> Optional[Labels]:
    """
    >>> github_ref_in_message(Commit({"owner": "x", "repository": "y", "_id": "12afbc4564ba", "message": "gh-123: bug"}))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit({"owner": "x", "repository": "y", "_id": "12afbc4564ba", "message": "gh 123"}))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit({"owner": "x", "repository": "y", "_id": "12afbc4564ba", "message": "GH 123: bug2"}))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit({"owner": "x", "repository": "y", "_id": "12afbc4564ba", "message": "GH123: wrong issue reference"})) is None
    True
    """
    return CommitLabel.BugFix if GITHUB_REF_RE.search(commit.message.raw) else None
