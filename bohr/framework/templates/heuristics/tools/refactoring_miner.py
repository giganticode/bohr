import subprocess
from dataclasses import dataclass
from typing import List

import jsons

from bohr.framework import SOFTWARE_DIR
from bohr.framework.artifacts.commit import Commit
from bohr.framework.templates.heuristics.tool import Tool

REFACTORING_MINER_PATH = (
    SOFTWARE_DIR
    / "RefactoringMiner"
    / "build"
    / "distributions"
    / "RefactoringMiner-2.0.3"
    / "bin"
)


@dataclass
class RefactoringMinerCommit:
    repository: str
    sha1: str
    url: str
    refactorings: List


@dataclass
class RefactoringMinerOutput:
    commits: List[RefactoringMinerCommit]


# TODO do we have such method anywhere
def get_full_github_url(author: str, repo: str) -> str:
    return f"https://github.com/{author}/{repo}"


class RefactoringMiner(Tool):
    def check_installed(self):
        pass

    def run(self, commit: Commit) -> RefactoringMinerOutput:
        url = get_full_github_url(commit.owner, commit.repository)
        cmd = ["./RefactoringMiner", "-gc", url, commit.sha, "1000"]

        result = subprocess.run(
            cmd, cwd=REFACTORING_MINER_PATH, capture_output=True, check=True
        )

        output = result.stdout.decode()
        print(output)
        return jsons.loads(output, cls=RefactoringMinerOutput)
