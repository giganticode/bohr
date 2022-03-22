from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def wip_keyword_in_message(commit: Commit) -> Optional[Labels]:
    if "wip" in commit.message.raw.lower():
        return CommitLabel.Feature
