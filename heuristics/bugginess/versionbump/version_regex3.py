import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel

VERSION_REGEX3 = re.compile(r"-rc")


@Heuristic(Commit)
def version_regex3(commit: Commit) -> Optional[Labels]:
    return (
        CommitLabel.VersionBump if VERSION_REGEX3.search(commit.message.raw) else None
    )
