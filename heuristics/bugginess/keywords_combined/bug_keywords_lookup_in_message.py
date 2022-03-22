from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=[
        ["issue", "unsynchron", "unclos", "endless", "outofbound", "of bound", "garbag", "repair", "not return", "deadlock", "dead lock", "defect", "corrupt", "concurr", "unexpect", "race condit", "inconsist", "unabl", "incomplet", "infinit", "mistak", "unknown", "leak", "nullpointer", "npe", "null pointer", "bad", "timeout", "not work", "loop", "threw", "throw", "incorrect", "invalid", "crash" ],
        ["broken", "properli", "wrong", "prevent", "ensur", "except", "minor"],
        ["problem",  "disabl", "resolv", "solv", "patch"],
        ["fail", "failur", "fault", "handl", "correct", "correctli"],
        ["error", "bug", "bugg"],
        ["close"],
        ["bugfix", "fix", "hotfix", "quickfix", "small fix"],
    ],
    name_pattern="bug_message_keyword_combined_%1",
)
def bug_keywords_lookup_in_message_combined(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.BugFix
    return None
