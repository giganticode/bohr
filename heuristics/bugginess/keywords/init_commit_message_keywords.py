from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


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
) -> Optional[OneOrManyLabels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.InitialCommit
    return None
