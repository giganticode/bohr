from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.collection.heuristictypes.keywords import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels


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
