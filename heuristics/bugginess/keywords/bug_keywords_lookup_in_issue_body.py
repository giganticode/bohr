from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.heuristictypes import KeywordHeuristics
from bohrapi.util.misc import NgramSet
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


@KeywordHeuristics(
    Commit,
    keywords=[
        "bad",
        "broken",
        ["bug", "bugg"],
        "close",
        ["correct", "correctli"],
        "corrupt",
        "crash",
        "defect",
        "disabl",
        "endless",
        "ensur",
        "error",
        "except",
        ["fail", "failur", "fault"],
        ["bugfix", "fix", "hotfix", "quickfix", "small fix"],
        "garbag",
        "handl",
        "incomplet",
        "inconsist",
        "incorrect",
        "infinit",
        "invalid",
        "issue",
        "leak",
        "loop",
        "minor",
        "mistak",
        ["nullpointer", "npe", "null pointer"],
        "not work",
        "not return",
        ["outofbound", "of bound"],
        "patch",
        "prevent",
        "problem",
        "properli",
        "repair",
        ["resolv", "solv"],
        ["threw", "throw"],
        "timeout",
        "unabl",
        "unclos",
        "unexpect",
        "unknown",
        "unsynchron",
        "wrong",
    ],
    name_pattern="bug_issue_body_keyword_%1",
)
def bug_keywords_lookup_in_issue_body(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_ngrams(keywords):
        return CommitLabel.BugFix
    return None
