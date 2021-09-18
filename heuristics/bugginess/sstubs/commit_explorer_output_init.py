from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels


@Heuristic(Commit)
def commit_explorer_output_init(commit: Commit) -> Optional[Labels]:
    try:
        if commit.commit_explorer_data is None:
            return None

        if (
            "special_commit_finder/0_1" in commit.commit_explorer_data
            and commit.commit_explorer_data["special_commit_finder/0_1"]["initial"]
        ):
            return l.CommitLabel.InitialCommit
    except (CommitExplorerClientException, CommitNotFoundException) as ex:
        return None
