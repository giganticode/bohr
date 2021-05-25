from typing import Optional

from bohr.collection.artifacts import Commit
from bohr.core import Heuristic
from bohr.labeling.labelset import Labels


@Heuristic(Commit)
def manual_labels(commit: Commit) -> Optional[Labels]:
    return commit.labels[0] if commit.labels else None