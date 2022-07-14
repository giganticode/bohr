import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel

VERSION_CHANGE_REGEX = re.compile(r"\.</eq><re>\d+<to>\d+</re>")


@Heuristic(Commit)
def contains_digit_replacement_change(commit: Commit) -> Optional[OneOrManyLabels]:
    """
    >>> VERSION_CHANGE_REGEX.search("<eq>4.</eq><re>11<to>12</re>")
    <re.Match object; span=(5, 28), match='.</eq><re>11<to>12</re>'>
    """
    for file in commit.commit_files:
        if file.changes is not None and VERSION_CHANGE_REGEX.search(file.changes):
            return CommitLabel.VersionBump
    return None
