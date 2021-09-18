from typing import Optional

from bohrapi.collection.artifacts import Commit
from bohrapi.collection.heuristictypes.keywords import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels


@KeywordHeuristics(
    Commit,
    keywords=["enhancement", "feature", "request", "refactor", "renovate", "new"],
    name_pattern="bugless_issue_label_keyword_%1",
)
def bugless_keywords_lookup_in_issue_label(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_label(keywords):
        return l.CommitLabel.NonBugFix
    return None
