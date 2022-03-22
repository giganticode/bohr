import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel

VERSION_REGEX = re.compile(r"v\d+\..*", flags=re.I)

VERSION_CHANGE_REGEX = re.compile(r"\.</eq><re>\d+<to>\d+</re>")


@Heuristic(Commit)
def version_regex(commit: Commit) -> Optional[Labels]:
    return CommitLabel.VersionBump if VERSION_REGEX.search(commit.message.raw) else None
