import re
from typing import Optional

from bohr.collection.artifacts import Commit
from bohr.core import Heuristic
from bohr.labeling.labelset import Labels
from labels import CommitLabel


@Heuristic(Commit)
def no_files_have_modified_status(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) == 0 or commit.commit_files[0].status == "empty":
        return None
    for file in commit.commit_files:
        if file.status == "modified":
            return None
    return CommitLabel.NonBugFix


@Heuristic(Commit)
def bug_if_only_changed_lines_in_one_code_file(commit: Commit) -> Optional[Labels]:
    if (
        len(commit.commit_files) == 1
        and commit.commit_files[0].status == "modified"
        and not isinstance(commit.commit_files[0].filename, float)
        and commit.commit_files[0].filename.split(".")[-1]
        in [*code_extensions, *passive_code_extensions]
        and commit.commit_files[0].changes
        and commit.commit_files[0].no_added_lines()
        and commit.commit_files[0].no_removed_lines()
    ):
        return CommitLabel.BugFix
    return None


@Heuristic(Commit)
def bugless_if_at_least_5_added_files(commit: Commit) -> Optional[Labels]:
    added_count = 0
    for file in commit.commit_files:
        if file.status == "added":
            added_count += 1
    return CommitLabel.NonBugFix if added_count >= 5 else None


@Heuristic(Commit)
def bugless_if_one_added_file(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) == 1 and commit.commit_files[0].status == "added":
        return CommitLabel.NonBugFix
    return None


@Heuristic(Commit)
def bugless_if_at_least_2_removed_files(commit: Commit) -> Optional[Labels]:
    removed_count = 0
    for file in commit.commit_files:
        if file.status == "removed":
            removed_count += 1
    return CommitLabel.NonBugFix if removed_count >= 2 else None


@Heuristic(Commit)
def bugless_if_one_removed_file(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) == 1 and commit.commit_files[0].status == "removed":
        return CommitLabel.NonBugFix
    return None


@Heuristic(Commit)
def refactoring_if_at_least_2_renamed(commit: Commit) -> Optional[Labels]:
    renamed_count = 0
    for file in commit.commit_files:
        if file.status == "renamed":
            renamed_count += 1
    return CommitLabel.Refactoring if renamed_count >= 2 else None


code_extensions = [
    "js",
    "java",
    "py",
    "php",
    "cpp",
    "h",
    "rb",
    "ts",
    "c",
    "go",
    "css",
    "cs",
    "scss",
    "jsx",
    "m",
    "less",
    "sh",
    "scala",
    "cc",
    "coffee",
    "F90",
    "hpp",
    "inc",
    "sql",
    "erb",
    "tsx",
    "kt",
    "Makefile",
    "groovy",
    "hbs",
    "swift",
    "hh",
    "twig",
    "haml",
    "hs",
    "scssc",
]
ignore_extensions = ["gitignore"]
config_extensions = [
    "yaml",
    "yml",
    "gradle",
    "in",
    "properties",
    "conf",
    "csproj",
    "ini",
    "config",
]
passive_code_extensions = [
    *ignore_extensions,
    *config_extensions,
    "xml",
    "html",
    "json",
    "htm",
]
binary_extensions = [
    "png",
    "po",
    "jpg",
    "gif",
    "tgz",
    "gz",
    "jar",
    "mo",
    "slj",
    "class",
    "gem",
    "map",
    "pdf",
    "ttf",
    "aw",
]
generated_text_extensions = ["out"]
doc_text_extensions = [
    "markdown",
    "md",
    "rst",
    "adoc",
]
non_code_extensions = [
    *binary_extensions,
    *generated_text_extensions,
    *doc_text_extensions,
    "txt",
    "svg",
    "lock",
    "LICENSE",
    "csv",
]


@Heuristic(Commit)
def bugless_if_not_code_files(commit: Commit) -> Optional[Labels]:
    file_found = False
    for file in commit.commit_files:
        if isinstance(file.filename, float):
            continue  # TODO filename is NaN if it's not given <- needs to be fixed
        if file.filename.split(".")[-1] in [*code_extensions, *passive_code_extensions]:
            # TODO move filetype logic to CommitFile artifact?
            return None
        else:
            file_found = True
    return CommitLabel.NonBugFix if file_found else None


@Heuristic(Commit)
def buggless_if_many_lines_changed(commit: Commit) -> Optional[Labels]:
    sum = 0
    for file in commit.commit_files:
        if file.changes:
            sum += len(file.changes)
    return CommitLabel.NonBugFix if sum > 5000 else None


@Heuristic(Commit)
def bugless_if_many_files_changes(commit: Commit) -> Optional[Labels]:
    if len(commit.commit_files) > 15:
        return CommitLabel.NonBugFix
    else:
        return None


@Heuristic(Commit)
def all_files_test_add(commit: Commit) -> Optional[Labels]:
    TEST_FILE_REGEX = re.compile(r"test", flags=re.I)
    if len(commit.commit_files) == 0:
        return None

    for file in commit.commit_files:

        def only_additions():
            return not (
                not file.changes or "<re>" in file.changes or "<del>" in file.changes
            )

        if not (
            TEST_FILE_REGEX.match(str(file.filename))
            and (file.status == "added" or only_additions())
        ):
            return None
    return CommitLabel.TestAdd


@Heuristic(Commit)
def all_files_test_fix(commit: Commit) -> Optional[Labels]:
    TEST_FILE_REGEX = re.compile(r"test", flags=re.I)
    if len(commit.commit_files) == 0:
        return None

    for file in commit.commit_files:
        if not (
            TEST_FILE_REGEX.match(str(file.filename))
            and file.status == "modified"
            and file.changes
            and "<re>" in file.changes
        ):
            return None
    return CommitLabel.TestFix
