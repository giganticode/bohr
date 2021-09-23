from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=["update dependenc"],
    name_pattern="dependency_bump_message_keyword_%1",
)
def dependency_bump_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.DependencyVersionBump
    return None
