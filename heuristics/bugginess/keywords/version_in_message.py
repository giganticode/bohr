import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel

VERSION_RE = re.compile(r"v\d+.*", flags=re.I)


@Heuristic(Commit)
def version_in_message(commit: Commit) -> Optional[OneOrManyLabels]:
    return CommitLabel.NonBugFix if VERSION_RE.search(commit.message.raw) else None
