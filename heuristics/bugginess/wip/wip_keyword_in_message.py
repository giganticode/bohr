from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def wip_keyword_in_message(commit: Commit) -> Optional[OneOrManyLabels]:
    if "wip" in commit.message.raw.lower():
        return CommitLabel.Feature
