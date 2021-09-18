from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.collection.heuristictypes.keywords import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels


@KeywordHeuristics(
    Commit,
    keywords=["update dependenc"],
    name_pattern="dependency_bump_message_keyword_%1",
)
def dependency_bump_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.DependencyVersionBump
    return None
