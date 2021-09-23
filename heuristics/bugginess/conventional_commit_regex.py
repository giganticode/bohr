import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel

example1 = """feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
"""

example2 = """refactor!: drop support for Node 6
"""

example3 = """refactor!: drop support for Node 6

BREAKING CHANGE: refactor to use JavaScript features not available in Node 6.
"""

example4 = """docs: correct spelling of CHANGELOG
"""

example5 = """feat(lang): add polish language
"""

example6 = """fix: correct minor typos in code

see the issue for details

on typos fixed.

Reviewed-by: Z
Refs #133
"""

REGEX = re.compile(
    r"\A(((Initial commit)|(Merge [^\r\n]+)|"
    r"((build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\(\w+\))?!?: [^\r\n]+"
    r"((\r|\n|\r\n)((\r|\n|\r\n)[^\r\n]+)+)*"
    r")"
    r")(\r|\n|\r\n)?)"
)


@Heuristic(Commit)
def conventional_commit_regex(commit: Commit) -> Optional[Labels]:
    """
    >>> conventional_commit_regex(Commit('a', 'a', '1df23', example1))
    CommitLabel.Feature
    >>> conventional_commit_regex(Commit('a', 'a', '1df23', example2))
    CommitLabel.Refactoring
    >>> conventional_commit_regex(Commit('a', 'a', '1df23', example3))
    CommitLabel.Refactoring
    >>> conventional_commit_regex(Commit('a', 'a', '1df23', example4))
    CommitLabel.DocChange
    >>> conventional_commit_regex(Commit('a', 'a', '1df23', example5))
    CommitLabel.Feature
    >>> conventional_commit_regex(Commit('a', 'a', '1df23', example6))
    CommitLabel.BugFix
    """
    m = REGEX.match(commit.message.raw)
    if m is None:
        return None
    type = m.groups()[5]
    if type == "fix":
        return CommitLabel.BugFix
    elif type == "feat":
        return CommitLabel.Feature
    elif type == "refactor":
        return CommitLabel.Refactoring
    elif type == "docs":
        return CommitLabel.DocChange
    else:
        return None
    # TODO add more types
