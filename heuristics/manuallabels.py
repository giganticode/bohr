from typing import Optional

from bohr.artifacts.commit import Commit
from bohr.decorators import Heuristic
from bohr.labels.labelset import Labels


@Heuristic(Commit)
def manual_labels(commit: Commit) -> Optional[Labels]:
    return commit.labels[0] if commit.labels else None