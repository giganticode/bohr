from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=["enhancement", "feature", "request", "refactor", "renovate", "new"],
    name_pattern="bugless_issue_label_keyword_%1",
)
def bugless_keywords_lookup_in_issue_label(
    commit: Commit, keywords: NgramSet
) -> Optional[OneOrManyLabels]:
    if commit.issues_match_label(keywords):
        return CommitLabel.NonBugFix
    return None
