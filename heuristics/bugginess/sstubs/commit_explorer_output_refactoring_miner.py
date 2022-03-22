from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def commit_explorer_output_refactoring_miner(commit: Commit) -> Optional[Labels]:
    if "refactoring_miner/2_1_0" in commit.raw_data:
        if commit.raw_data["refactoring_miner/2_1_0"]:
            if commit.raw_data["refactoring_miner/2_1_0"]["status"] == "ok":
                if len(commit.raw_data["refactoring_miner/2_1_0"]["refactorings"]) == 1:
                    if commit.raw_data["refactoring_miner/2_1_0"]["refactorings"][0][
                        "type"
                    ] in ["Move Class"]:
                        return CommitLabel.Refactoring
