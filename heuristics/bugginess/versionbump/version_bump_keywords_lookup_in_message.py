from typing import Optional

import labels as l
from bohrapi.collection.artifacts import Commit
from bohrapi.collection.heuristictypes.keywords import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels


@KeywordHeuristics(
    Commit,
    keywords=[
        "bump",
        "to version",
        "bump to",
        "bump version" "upgrad version",
        "increment version",
        "increment to",
        "version increment",
        "version",
    ],
    name_pattern="bump_version_message_keyword_%1",
)
def version_bump_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.VersionBump
    return None
