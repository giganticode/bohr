from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=[
        "move",
        "refactor",
        "renam",
        "reorgan",
        "restructur",
        "rewrit",
        "simplif",
        "simplifi",
    ],
    name_pattern="bugless_message_keyword_%1",
)
def bugless_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[OneOrManyLabels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.Refactoring
    return None
