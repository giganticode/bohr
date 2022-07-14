import re
from typing import Optional

from bohrapi.artifacts import Commit
from bohrapi.core import Heuristic
from bohrlabels.core import OneOrManyLabels
from bohrlabels.labels import CommitLabel


@Heuristic(Commit)
def all_files_test_add(commit: Commit) -> Optional[OneOrManyLabels]:
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
