from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels


@Heuristic(Commit)
def commit_explorer_output_refactoring_miner(commit: Commit) -> Optional[Labels]:
    if commit.commit_explorer_data is None:
        return None

    data = commit.commit_explorer_data
    if "refactoring_miner/2_1_0" in data:
        if data["refactoring_miner/2_1_0"]:
            if data["refactoring_miner/2_1_0"]["status"] == "ok":
                if len(data["refactoring_miner/2_1_0"]["refactorings"]) == 1:
                    if data["refactoring_miner/2_1_0"]["refactorings"][0]["type"] in [
                        "Move Class"
                    ]:
                        print("Contains refactoring")
                        return l.CommitLabel.Refactoring
