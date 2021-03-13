import re
from typing import Optional

from bohr.artifacts.commit import Commit
from bohr.cli import apply_heuristics
from bohr.decorators import Heuristic
from bohr.labels.labelset import Labels
from bohr.nlp_utils import NgramSet
from bohr.templates.heuristics.keywords import KeywordHeuristics
from labels import *


@KeywordHeuristics(Commit, "bug", name_pattern="bug_message_keyword_%1")
def bug_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.BugFix
    return None


@KeywordHeuristics(Commit, "bugless", name_pattern="bugless_message_keyword_%1")
def bugless_keywords_lookup_in_message(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.message.match_ngrams(keywords):
        return CommitLabel.NonBugFix
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
    return CommitLabel.BugFix if GITHUB_REF_RE.search(commit.message.raw) else None


@Heuristic(Commit)
def version_in_message(commit: Commit) -> Optional[Labels]:
    return CommitLabel.NonBugFix if VERSION_RE.search(commit.message.raw) else None


@KeywordHeuristics(Commit, "bug.issue_label", name_pattern="bug_issue_label_keyword_%1")
def bug_keywords_lookup_in_issue_label(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_label(keywords):
        return CommitLabel.BugFix
    return None


@KeywordHeuristics(
    Commit, "bugless.issue_label", name_pattern="bugless_issue_label_keyword_%1"
)
def bugless_keywords_lookup_in_issue_label(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_label(keywords):
        return CommitLabel.NonBugFix
    return None


@KeywordHeuristics(Commit, "bug", name_pattern="bug_issue_body_keyword_%1")
def bug_keywords_lookup_in_issue_body(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_ngrams(keywords):
        return CommitLabel.BugFix
    return None


@KeywordHeuristics(Commit, "bugless", name_pattern="bugless_issue_body_keyword_%1")
def bugless_keywords_lookup_in_issue_body(
    commit: Commit, keywords: NgramSet
) -> Optional[Labels]:
    if commit.issues_match_ngrams(keywords):
        return CommitLabel.NonBugFix
    return None
