from typing import Optional

import labels as l
from bohr.collection.artifacts import Commit
from bohr.collection.heuristictypes.keywords import KeywordHeuristics
from bohr.labeling.labelset import Labels
from bohr.util.misc import NgramSet


@KeywordHeuristics(
    Commit,
    keywords=[
        "init",
        "initial",
        "first",
    ],
    name_pattern="init_commit_message_keyword_%1",
)
def init_commit_message_keywords(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.InitialCommit
    return None
