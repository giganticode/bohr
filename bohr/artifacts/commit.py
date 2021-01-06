from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from typing import List, Set

import pandas as pd

from bohr import PROJECT_DIR, TRAIN_DIR
from bohr.artifacts.commit_file import CommitFile
from bohr.artifacts.commit_message import CommitMessage
from bohr.artifacts.core import Artifact
from bohr.artifacts.issue import Issue
from bohr.nlp_utils import NgramSet

ISSUES_FILE = PROJECT_DIR / "data/train/bug_sample_issues.csv"
CHANGES_FILE = PROJECT_DIR / "data/train/bug_sample_files.csv"
COMMITS_FILE = PROJECT_DIR / "data/train/bug_sample.csv"


@dataclass
class Commit(Artifact):

    owner: str
    repository: str
    sha: str
    raw_message: str
    message: CommitMessage = field(init=False)

    def __post_init__(self):
        self.message = CommitMessage(self.raw_message)

    class Cache:
        @lru_cache(maxsize=8)
        def __load_df(self, type: str, owner: str, repository: str):
            path = TRAIN_DIR / type / owner / f"{repository}.csv"
            if path.is_file():
                return pd.read_csv(
                    path,
                    index_col=["sha"],
                    keep_default_na=False,
                    dtype={"labels": "str"},
                )
            else:
                return None

        @cached_property
        def __issues_df(self):
            return pd.read_csv(
                ISSUES_FILE,
                index_col=["owner", "repository", "sha"],
                keep_default_na=False,
                dtype={"labels": "str"},
            )

        @cached_property
        def __files_df(self):
            return pd.read_csv(CHANGES_FILE, index_col=["owner", "repository", "sha"])

        def get_resources_from_file(
            self, type: str, owner: str, repository: str, sha: str
        ):
            if type == "issues":
                df = self.__issues_df
            elif type == "files":
                df = self.__files_df
            else:
                raise ValueError("invalid resources type")

            try:
                return df.loc[[(owner, repository, sha)]]
            except KeyError:
                return None

        def get_resources_from_dir(
            self, type: str, owner: str, repository: str, sha: str
        ):
            df = self.__load_df(type, owner, repository)
            try:
                return df.loc[[sha]]
            except KeyError:
                return None

        def get_files(self, owner: str, repository: str, sha: str):
            if CHANGES_FILE:
                return self.get_resources_from_file("files", owner, repository, sha)
            else:
                return self.get_resources_from_dir("files", owner, repository, sha)

        def get_issues(self, owner: str, repository: str, sha: str):
            if ISSUES_FILE:
                return self.get_resources_from_file("issues", owner, repository, sha)
            else:
                return self.get_resources_from_dir("issues", owner, repository, sha)

    _cache = Cache()

    def __hash__(self):
        return hash((self.owner, self.repository, self.sha))

    @cached_property
    def files(self) -> List[CommitFile]:
        df = self._cache.get_files(self.owner, self.repository, self.sha)
        files = []

        if df is not None:
            for file in df.itertuples(index=False):
                files.append(
                    CommitFile(
                        file.filename,
                        file.status,
                        file.patch if not isinstance(file.patch, float) else None,
                        file.change if not isinstance(file.change, float) else None,
                    )
                )
        return files

    @cached_property
    def issues(self) -> List[Issue]:
        df = self._cache.get_issues(self.owner, self.repository, self.sha)
        issues = []

        if df is not None:
            for issue in df.itertuples():
                labels = issue.labels
                labels = list(filter(None, labels.split(", ")))

                issues.append(Issue(issue.title, issue.body, labels))

        return issues

    def issues_match_label(self, stemmed_labels: Set[str]) -> bool:
        for issue in self.issues:
            if not issue.stemmed_labels.isdisjoint(stemmed_labels):
                return True
        return False

    def issues_match_ngrams(self, stemmed_keywords: NgramSet) -> bool:
        for issue in self.issues:
            if not issue.stemmed_ngrams.isdisjoint(stemmed_keywords):
                return True
        return False
