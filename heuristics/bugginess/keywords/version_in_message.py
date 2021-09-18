import re
from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels

VERSION_RE = re.compile(r"v\d+.*", flags=re.I)


@Heuristic(Commit)
def version_in_message(commit: Commit) -> Optional[Labels]:
    return l.CommitLabel.NonBugFix if VERSION_RE.search(commit.message.raw) else None
