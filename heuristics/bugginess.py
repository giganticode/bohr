import re
from typing import Optional

import labels as l
from bohr.artifacts.commit import Commit
from bohr.decorators import Heuristic
from bohr.labels.labelset import Labels
from bohr.nlp_utils import NgramSet
from bohr.templates.heuristics.keywords import KeywordHeuristics


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
    name_pattern="bug_message_keyword_%1",
)
def bug_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.BugFix
    return None


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
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.ConcurrencyBugFix
    return None


@KeywordHeuristics(
    Commit,
    keywords=[
        "abil",
        "ad",
        "add",
        "addit",
        "allow",
        "analysi",
        "avoid",
        "baselin",
        "beautification",
        "benchmark",
        "better",
        "bump",
        "chang log",
        ["clean", "cleanup"],
        "comment",
        "complet",
        "configur chang",
        "consolid",
        "convert",
        "coverag",
        "create",
        "deprec",
        "develop",
        ["doc", "document", "javadoc"],
        "drop",
        "enhanc",
        "exampl",
        "exclud",
        "expand",
        "extendgener",
        "featur",
        "forget",
        "format",
        "gitignor",
        "idea",
        "implement",
        "improv",
        "includ",
        "info",
        "intorduc",
        "limit",
        "log",
        "migrat",
        "minim",
        "modif",
        "move",
        "new",
        "note",
        "opinion",
        ["optim", "optimis"],
        "pass test",
        "perf test",
        "perfom test",
        "perform",
        "plugin",
        "polish",
        "possibl",
        "prepar",
        "propos",
        "provid",
        "publish",
        "readm",
        "reduc",
        "refactor",
        "refin",
        "reformat",
        "regress test",
        "reimplement",
        "release",
        "remov",
        "renam",
        "reorgan",
        "replac",
        "restrict",
        "restructur",
        "review",
        "rewrit",
        "rid",
        "set up",
        "simplif",
        "simplifi",
        ["speedup", "speed up"],
        "stage",
        "stat",
        "statist",
        "support",
        "switch",
        "test",
        "test coverag",
        "test pass",
        "todo",
        "tweak",
        "unit",
        "unnecessari",
        "updat",
        "upgrad",
        "version",
    ],
    name_pattern="bugless_message_keyword_%1",
)
def bugless_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return l.CommitLabel.NonBugFix
    return None


GITHUB_REF_RE = re.compile(r"gh(-|\s)\d+", flags=re.I)
VERSION_RE = re.compile(r"v\d+.*", flags=re.I)


@Heuristic(Commit)
def github_ref_in_message(commit: Commit) -> Optional[Labels]:
    """
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "gh-123: bug"))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "gh 123"))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "GH 123: bug2"))
    CommitLabel.BugFix
    >>> github_ref_in_message(Commit("x", "y", "12afbc4564ba", "GH123: wrong issue reference")) is None
    True
    """
    return l.CommitLabel.BugFix if GITHUB_REF_RE.search(commit.message.raw) else None


@Heuristic(Commit)
def version_in_message(commit: Commit) -> Optional[Labels]:
    return l.CommitLabel.NonBugFix if VERSION_RE.search(commit.message.raw) else None


@KeywordHeuristics(
    Commit,
    keywords=["bug", "fixed", "fix", "error"],
    name_pattern="bug_issue_label_keyword_%1",
)
def bug_keywords_lookup_in_issue_label(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_label(keywords):
        return l.CommitLabel.BugFix
    return None


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


@KeywordHeuristics(
    Commit,
    keywords=[
        "bad",
        "broken",
        ["bug", "bugg"],
        "close",
        "concurr",
        ["correct", "correctli"],
        "corrupt",
        "crash",
        ["deadlock", "dead lock"],
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
        "race condit",
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
        return l.CommitLabel.BugFix
    return None


@KeywordHeuristics(
    Commit,
    keywords=[
        "abil",
        "ad",
        "add",
        "addit",
        "allow",
        "analysi",
        "avoid",
        "baselin",
        "beautification",
        "benchmark",
        "better",
        "bump",
        "chang log",
        ["clean", "cleanup"],
        "comment",
        "complet",
        "configur chang",
        "consolid",
        "convert",
        "coverag",
        "create",
        "deprec",
        "develop",
        ["doc", "document", "javadoc"],
        "drop",
        "enhanc",
        "exampl",
        "exclud",
        "expand",
        "extendgener",
        "featur",
        "forget",
        "format",
        "gitignor",
        "idea",
        "implement",
        "improv",
        "includ",
        "info",
        "intorduc",
        "limit",
        "log",
        "migrat",
        "minim",
        "modif",
        "move",
        "new",
        "note",
        "opinion",
        ["optim", "optimis"],
        "pass test",
        "perf test",
        "perfom test",
        "perform",
        "plugin",
        "polish",
        "possibl",
        "prepar",
        "propos",
        "provid",
        "publish",
        "readm",
        "reduc",
        "refactor",
        "refin",
        "reformat",
        "regress test",
        "reimplement",
        "release",
        "remov",
        "renam",
        "reorgan",
        "replac",
        "restrict",
        "restructur",
        "review",
        "rewrit",
        "rid",
        "set up",
        "simplif",
        "simplifi",
        ["speedup", "speed up"],
        "stage",
        "stat",
        "statist",
        "support",
        "switch",
        "test",
        "test coverag",
        "test pass",
        "todo",
        "tweak",
        "unit",
        "unnecessari",
        "updat",
        "upgrad",
        "version",
    ],
    name_pattern="bugless_issue_body_keyword_%1",
)
def bugless_keywords_lookup_in_issue_body(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_ngrams(keywords):
        return l.CommitLabel.NonBugFix
    return None
