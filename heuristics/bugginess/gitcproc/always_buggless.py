from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def gitcproc_buggless_no_keywords_matched(
        commit: Commit
) -> Optional[Labels]:
    for ngram in [
        "bug",
        "fix",
        "issu",
        "mistak",
        "incorrect",
        "fault",
        "defect",
        "flaw",
        "type",
    ]:
        if commit.message.match_ngrams({ngram}):
            return None
    return CommitLabel.NonBugFix
