from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=[
        "bug",
        "fix",
        "issu",
        "mistak",
        "incorrect",
        "fault",
        "defect",
        "flaw",
        "type",
    ],
    name_pattern="gitcproc_message_keyword_%1",
)
def gitcproc_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[OneOrManyLabels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.BugFix
    return None
