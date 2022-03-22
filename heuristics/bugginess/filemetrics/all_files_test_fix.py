import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import Labels
from bohrlabels.labels import CommitLabel


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
