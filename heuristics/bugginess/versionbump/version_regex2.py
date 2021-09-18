import re
from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels

VERSION_REGEX2 = re.compile(r"\d-SNAPSHOT")


@Heuristic(Commit)
def version_regex2(commit: Commit) -> Optional[Labels]:
    return (
        l.CommitLabel.VersionBump if VERSION_REGEX2.search(commit.message.raw) else None
    )
