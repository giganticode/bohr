import re
from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels

VERSION_REGEX = re.compile(r"v\d+\..*", flags=re.I)

VERSION_CHANGE_REGEX = re.compile(r"\.</eq><re>\d+<to>\d+</re>")


@Heuristic(Commit)
def version_regex(commit: Commit) -> Optional[Labels]:
    return (
        l.CommitLabel.VersionBump if VERSION_REGEX.search(commit.message.raw) else None
    )
