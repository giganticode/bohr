from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def commit_explorer_output_init(commit: Commit) -> Optional[OneOrManyLabels]:
    if (
        "special_commit_finder/0_1" in commit.raw_data
        and "initial" in commit.raw_data["special_commit_finder/0_1"]
        and commit.raw_data["special_commit_finder/0_1"]["initial"]
    ):
        return CommitLabel.InitialCommit
