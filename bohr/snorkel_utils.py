from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property, lru_cache
from typing import Optional, List, Set, Mapping, Any, Tuple, Callable, Union

import pandas as pd
from cachetools import LRUCache
from nltk import bigrams
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

from snorkel.labeling import labeling_function, LabelingFunction
from snorkel.map import BaseMapper
from snorkel.preprocess import BasePreprocessor
from snorkel.types import DataPoint

from bohr import TRAIN_DIR, logger
from bohr.pipeline.args import get_heuristic_args

NgramSet = Set[Union[Tuple[str], str]]


class Label(Enum):
    BUG = 1
    BUGLESS = 0
    ABSTAIN = -1

_tokenizer = RegexpTokenizer(r"[\s_\.,%#/\?!\-\'\"\)\(\]\[\:;]", gaps=True)

def safe_tokenize(text: Any) -> Set[str]:
    if text is None: return set()
    if pd.isna(text): return set()

    tokens = _tokenizer.tokenize(str(text).lower())
    return tokens


@dataclass
class Issue:
    title: str
    body: str
    labels: List[str]

    @cached_property
    def stemmed_labels(self) -> Set[str]:
        stemmer = PorterStemmer()
        return set([stemmer.stem(l) for l in self.labels])

    @cached_property
    def tokens(self) -> Set[str]:
        if self.body is None: return set()
        return safe_tokenize(self.body)

    @cached_property
    def ordered_stems(self) -> List[str]:
        stemmer = PorterStemmer()
        return [stemmer.stem(w) for w in self.tokens]

    @cached_property
    def stemmed_ngrams(self) -> NgramSet:
        return set(self.ordered_stems).union(set(bigrams(self.ordered_stems)))


class Issues:
    def __init__(self, issues):
        self.__issues = issues

    def __len__(self) -> int:
        return len(self.__issues)

    def __getitem__(self, idx) -> Issue:
        return self.__issues[idx]

    def match_label(self, stemmed_labels: Set[str]) -> bool:
        for issue in self.__issues:
            if not issue.stemmed_labels.isdisjoint(stemmed_labels): return True
        return False

    def match_ngrams(self, stemmed_keywords: NgramSet) -> bool:
        for issue in self.__issues:
            if not issue.stemmed_ngrams.isdisjoint(stemmed_keywords): return True
        return False



@dataclass
class CommitFile:
    filename: str
    status: str
    patch: Optional[str]
    changes: Optional[str]


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
        if self.raw is None: return set()
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

        @property
        def __args(self):
            return get_heuristic_args()

        @lru_cache(maxsize=8)
        def __load_df(self, type: str, owner: str, repository: str):
            path = TRAIN_DIR / type  / owner / f"{repository}.csv"
            if path.is_file():
                return pd.read_csv(path, index_col=['sha'], keep_default_na=False, dtype={'labels': 'str'})
            else:
                return None

        @cached_property
        def __issues_df(self):
            return pd.read_csv(self.__args.issues_file, index_col=['owner', 'repository', 'sha'],
                               keep_default_na=False, dtype={'labels': 'str'})

        @cached_property
        def __files_df(self):
            return pd.read_csv(self.__args.changes_file, index_col=['owner', 'repository', 'sha'])

        def get_resources_from_file(self, type: str, owner: str, repository: str, sha: str):
            if type == 'issues':
                df = self.__issues_df
            elif type == 'files':
                df = self.__files_df
            else:
               raise ValueError('invalid resources type')

            try:
                return df.loc[[(owner, repository, sha)]]
            except KeyError as e:
                return None

        def get_resources_from_dir(self, type: str, owner: str, repository: str, sha: str):
            df = self.__load_df(type, owner, repository)
            try:
                return df.loc[[sha]]
            except KeyError as e:
                return None

        def get_files(self, owner: str, repository: str, sha: str):
            if self.__args.changes_file:
                return self.get_resources_from_file('files', owner, repository, sha)
            else:
                return self.get_resources_from_dir('files', owner, repository, sha)

        def get_issues(self, owner: str, repository: str, sha: str):
            if self.__args.issues_file:
                return self.get_resources_from_file('issues', owner, repository, sha)
            else:
                return self.get_resources_from_dir('issues', owner, repository, sha)


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
            try:
                df = df.loc[[self.sha]]
                for file in df.itertuples():
                    files.append(CommitFile(file.filename, file.status, file.get('patch', None), file.get('change', None)))
            except (AttributeError) as e:
                logger.warn(f'Cannot add commit files:\n {df}')

        return CommitFiles(files)

    @cached_property
    def issues(self) -> Issues:
        df = self._cache.get_issues(self.owner, self.repository, self.sha)
        issues = []

        if df is not None:
            for issue in df.itertuples():
                labels = issue.labels
                labels = list(filter(None, labels.split(', ')))

                issues.append(Issue(issue.title, issue.body, labels))
        
        return Issues(issues)

class CommitMapper(BaseMapper):

    cache = LRUCache(512)

    def __init__(self) -> None:
        super().__init__('CommitMapper', [], memoize=False)

    def __call__(self, x: DataPoint) -> Optional[DataPoint]:
        key = (x.owner, x.repository, x.sha)
        if key in self.cache:
            return self.cache[key]

        commit = Commit(x.owner, x.repository, x.sha, x.message)
        self.cache[key] = commit

        return commit


class CommitLabelingFunction(LabelingFunction):
    def __init__(
        self,
        name: str,
        f: Callable[..., int],
        resources: Optional[Mapping[str, Any]] = None,
        pre: Optional[List[BasePreprocessor]] = None,
    ) -> None:
        if pre is None:
            pre = []
        pre.insert(0, CommitMapper())            
        super().__init__(name, f, resources, pre=pre)


class commit_lf(labeling_function):
    def __call__(self, f: Callable[..., Label]) -> LabelingFunction:
        name = self.name or f.__name__
        return CommitLabelingFunction(name=name, f=lambda *args: f(*args).value, resources=self.resources, pre=self.pre)
