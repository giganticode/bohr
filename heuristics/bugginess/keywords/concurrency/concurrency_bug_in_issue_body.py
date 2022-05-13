from typing import Optional

import bohrlabels.labels as l
from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels


@KeywordHeuristics(
    Commit,
    keywords=[
        "concurr",
        ["deadlock", "dead lock"],
        "race condit",
    ],
    name_pattern="concurrency_bug_keywords_in_message_%1",
)
def concurrency_bug_keywords_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_ngrams(keywords):
        return l.CommitLabel.ConcurrencyBugFix
    return None
