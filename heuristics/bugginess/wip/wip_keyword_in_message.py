from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrapi.labeling import Labels
from labels import CommitLabel


@Heuristic(Commit)
def wip_keyword_in_message(commit: Commit) -> Optional[Labels]:
    if "wip" in commit.message.raw.lower():
        return CommitLabel.Feature
