import re
from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels

VERSION_REGEX3 = re.compile(r"-rc")


@Heuristic(Commit)
def version_regex3(commit: Commit) -> Optional[Labels]:
    return (
        l.CommitLabel.VersionBump if VERSION_REGEX3.search(commit.message.raw) else None
    )
