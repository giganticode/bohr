import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel

VERSION_REGEX2 = re.compile(r"\d-SNAPSHOT")


@Heuristic(Commit)
def version_regex2(commit: Commit) -> Optional[OneOrManyLabels]:
    return (
        CommitLabel.VersionBump if VERSION_REGEX2.search(commit.message.raw) else None
    )
