from typing import Optional

import bohrlabels.labels as l
from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels


@KeywordHeuristics(
    Commit,
    keywords=[
        "beautification",
        "format",
        "reformat",
    ],
    name_pattern="reformatting_keywords_in_message_%1",
)
def reformatting_keywords_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.Reformatting
    return None
