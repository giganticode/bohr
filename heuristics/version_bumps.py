import re
from typing import Optional

import labels as l
from bohr.collection.artifacts import Commit
from bohr.collection.heuristictypes.keywords import KeywordHeuristics
from bohr.core import Heuristic
from bohr.labeling.labelset import Labels
from bohr.util.misc import NgramSet

VERSION_REGEX = re.compile(r"v\d+\..*", flags=re.I)
VERSION_REGEX2 = re.compile(r"\d-SNAPSHOT")
VERSION_REGEX3 = re.compile(r"-rc")

VERSION_CHANGE_REGEX = re.compile(r"\.</eq><re>\d+<to>\d+</re>")


@Heuristic(Commit)
def version_regex(commit: Commit) -> Optional[Labels]:
    return (
        l.CommitLabel.VersionBump if VERSION_REGEX.search(commit.message.raw) else None
    )


@Heuristic(Commit)
def version_regex2(commit: Commit) -> Optional[Labels]:
    return (
        l.CommitLabel.VersionBump if VERSION_REGEX2.search(commit.message.raw) else None
    )


@Heuristic(Commit)
def version_regex3(commit: Commit) -> Optional[Labels]:
    return (
        l.CommitLabel.VersionBump if VERSION_REGEX3.search(commit.message.raw) else None
    )


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


@Heuristic(Commit)
def maven_plugin_version_bump(commit: Commit) -> Optional[Labels]:
    if "[maven-release-plugin]" in commit.message.raw:
        return l.CommitLabel.VersionBump
    return None


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


@Heuristic(Commit)
def contains_python_version_file(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        if file.filename == ".python-version" and file.status == "modified":
            return l.CommitLabel.DependencyVersionBump
    return None


@Heuristic(Commit)
def contains_ruby_version_file(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        if file.filename == ".ruby-version" and file.status == "modified":
            return l.CommitLabel.DependencyVersionBump
    return None


@Heuristic(Commit)
def contains_package_lock_file(commit: Commit) -> Optional[Labels]:
    for file in commit.commit_files:
        if file.filename == "package-lock.json" and file.status == "modified":
            return l.CommitLabel.DependencyVersionBump
    return None


@Heuristic(Commit)
def contains_digit_replacement_change(commit: Commit) -> Optional[Labels]:
    """
    >>> VERSION_CHANGE_REGEX.search("<eq>4.</eq><re>11<to>12</re>")
    <re.Match object; span=(5, 28), match='.</eq><re>11<to>12</re>'>
    """
    for file in commit.commit_files:
        if file.changes is not None and VERSION_CHANGE_REGEX.search(file.changes):
            return l.CommitLabel.VersionBump
    return None


# @Heuristic(Commit)
# def long_message_not_version_bump(commit: Commit) -> Optional[Labels]:
#     if len(commit.message.raw) > 50:
#         return ~l.CommitLabel.VersionBump
#     else:
#         return None

# TODO another heuristic: return ~l.CommitLabel.VersionBump if too many files changed
