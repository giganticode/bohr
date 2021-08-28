from typing import Optional

from commitexplorer.client import CommitExplorerClientException, CommitNotFoundException

import labels as l
from bohr.collection.artifacts import Commit
from bohr.core import Heuristic
from bohr.labeling.labelset import Labels


@Heuristic(Commit)
def commit_explorer_output_merge(commit: Commit) -> Optional[Labels]:
    try:
        if commit.commit_explorer_data is None:
            return None

        if (
            "special_commit_finder/0_1" in commit.commit_explorer_data
            and commit.commit_explorer_data["special_commit_finder/0_1"]["merge"]
        ):
            return l.CommitLabel.Merge
    except (CommitExplorerClientException, CommitNotFoundException) as ex:
        return None


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


# @Heuristic(Commit)
# def commit_explorer_output_refactoring_miner(commit: Commit) -> Optional[Labels]:
#     if commit.commit_explorer_data is None:
#         return None
#
#     data = commit.commit_explorer_data
#     if "refactoring_miner/2_1_0" in data:
#         if data["refactoring_miner/2_1_0"]:
#             if data["refactoring_miner/2_1_0"]['status'] == 'ok':
#                 if len(data["refactoring_miner/2_1_0"]["refactorings"]) == 1:
#                     if data["refactoring_miner/2_1_0"]["refactorings"][0]["type"] in ['Move Class']:
#                         print("Contains refactoring")
#                         return l.CommitLabel.Refactoring


@Heuristic(Commit)
def commit_explorer_output_sstubs(commit: Commit) -> Optional[Labels]:
    try:
        if commit.commit_explorer_data is None:
            return None

        data = commit.commit_explorer_data
        if "mine_sstubs/head" in data and data["mine_sstubs/head"]:
            print("Contains bug")
            return l.CommitLabel.BugFix
    except (CommitExplorerClientException, CommitNotFoundException) as ex:
        return None
