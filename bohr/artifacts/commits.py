from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from typing import Optional, Set, List

import pandas as pd
from nltk import PorterStemmer, bigrams

from bohr import TRAIN_DIR, params
from bohr.nlp_utils import safe_tokenize, NgramSet
from bohr.artifacts.issues import Issue, Issues


@dataclass
class CommitFile:
    filename: str
    status: str
    patch: Optional[str]
    changes: Optional[str]

    def no_added_lines(self):
        return "<ins>" not in self.changes

    def no_removed_lines(self):
        return "<del>" not in self.changes


class CommitFiles:
    def __init__(self, files):
        self.__files = files

    def __len__(self) -> int:
        return len(self.__files)

    def __getitem__(self, idx) -> CommitFile:
        return self.__files[idx]


@dataclass
class CommitMessage:
    raw: str

    @cached_property
    def tokens(self) -> Set[str]:
        if self.raw is None:
            return set()
        return safe_tokenize(self.raw)

    @cached_property
    def ordered_stems(self) -> List[str]:
        stemmer = PorterStemmer()
        return [stemmer.stem(w) for w in self.tokens]

    @cached_property
    def stemmed_ngrams(self) -> NgramSet:
        return set(self.ordered_stems).union(set(bigrams(self.ordered_stems)))

    def match_ngrams(self, stemmed_keywords: NgramSet) -> bool:
        return not self.stemmed_ngrams.isdisjoint(stemmed_keywords)


@dataclass
class Commit:

    owner: str
    repository: str
    sha: str
    raw_message: str
    message: CommitMessage = field(init=False)

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
                params.ISSUES_FILE,
                index_col=["owner", "repository", "sha"],
                keep_default_na=False,
                dtype={"labels": "str"},
            )

        @cached_property
        def __files_df(self):
            return pd.read_csv(
                params.CHANGES_FILE, index_col=["owner", "repository", "sha"]
            )

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
            except KeyError as e:
                return None

        def get_resources_from_dir(
            self, type: str, owner: str, repository: str, sha: str
        ):
            df = self.__load_df(type, owner, repository)
            try:
                return df.loc[[sha]]
            except KeyError as e:
                return None

        def get_files(self, owner: str, repository: str, sha: str):
            if params.CHANGES_FILE:
                return self.get_resources_from_file("files", owner, repository, sha)
            else:
                return self.get_resources_from_dir("files", owner, repository, sha)

        def get_issues(self, owner: str, repository: str, sha: str):
            if params.ISSUES_FILE:
                return self.get_resources_from_file("issues", owner, repository, sha)
            else:
                return self.get_resources_from_dir("issues", owner, repository, sha)

    _cache = Cache()

    def __post_init__(self):
        self.message = CommitMessage(self.raw_message)

    def __hash__(self):
        return hash((self.owner, self.repository, self.sha))

    @cached_property
    def files(self) -> CommitFiles:
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
        return CommitFiles(files)

    @cached_property
    def issues(self) -> Issues:
        df = self._cache.get_issues(self.owner, self.repository, self.sha)
        issues = []

        if df is not None:
            for issue in df.itertuples():
                labels = issue.labels
                labels = list(filter(None, labels.split(", ")))

                issues.append(Issue(issue.title, issue.body, labels))

        return Issues(issues)
