from functools import wraps, cached_property, lru_cache
from typing import Optional, List, Set, Mapping, Any, Tuple
from snorkel.types import DataPoint

from bohr import TEST_DIR, TRAIN_DIR

from dataclasses import dataclass, field
from cachetools import LRUCache

import pandas as pd

import snorkel
from snorkel.labeling import labeling_function, LabelingFunction
from snorkel.preprocess import preprocessor
from snorkel.map import BaseMapper, LambdaMapper
from snorkel.map.core import MapFunction

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 
from nltk import bigrams

Label = int

BUG = 1
BUGLESS = 0
ABSTAIN = -1

def safe_word_tokenize(text: Any) -> Set[str]:
    if text is None: return set()
    if pd.isna(text): return set()

    return word_tokenize(str(text).lower())


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
        return safe_word_tokenize(self.body)

    @cached_property
    def stems(self) -> Set[str]:
        stemmer = PorterStemmer()
        return set([stemmer.stem(w) for w in self.tokens])

    @cached_property
    def stem_bigrams(self) -> Set[Tuple[str, str]]:
        return set(bigrams(self.stems))



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

    def match(self, stemmed_keywords: Set[str]) -> bool:
        for issue in self.__issues:
            if not issue.stems.isdisjoint(stemmed_keywords): return True
        return False

    def match_bigram(self, stemmed_bigrams: Set[Tuple[str, str]]) -> bool:
        for issue in self.__issues:
            if not issue.stem_bigrams.isdisjoint(stemmed_bigrams): return True
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
        return safe_word_tokenize(self.raw)

    @cached_property
    def stems(self) -> Set[str]:
        stemmer = PorterStemmer()
        return set([stemmer.stem(w) for w in self.tokens])

    @cached_property
    def stem_bigrams(self) -> Set[Tuple[str, str]]:
        return set(bigrams(self.stems))

    def match(self, stemmed_keywords: Set[str]) -> bool:
        return not self.stems.isdisjoint(stemmed_keywords)

    def match_bigram(self, stemmed_bigrams: Set[Tuple[str, str]]) -> bool:
        return not self.stems.isdisjoint(stemmed_bigrams)



@dataclass
class Commit:

    owner: str
    repository: str
    sha: str
    raw_message: str
    message: CommitMessage = field(init=False)

    def __post_init__(self):
        self.message = CommitMessage(self.raw_message)

    @lru_cache(maxsize=4)
    def __load_df(self, type: str, owner: str, repository: str):
        path = TRAIN_DIR / type  / owner / f"{repository}.csv"
        if path.is_file():
            return pd.read_csv(path, index_col=['sha'])
        else:
            return None

    def __hash__(self):
        return hash((self.owner, self.repository, self.sha))

    @cached_property
    def files(self) -> CommitFiles:
        df = self.__load_df('files', self.owner, self.repository)
        files = []

        if df is not None:
            try:
                df = df.loc[[self.sha]]
                for sha, file in df.iterrows():
                    files.append(CommitFile(file.filename, file.status, file.get('patch', None), file.get('change', None)))
            except KeyError as e:
                pass

        return CommitFiles(files)

    @cached_property
    def issues(self) -> Issues:
        df = self.__load_df('issues', self.owner, self.repository)
        issues = []

        if df is not None:
            df = df.loc[[self.sha]]
            for sha, issue in df.iterrows():
                labels = issue.labels.split(', ')
                issues.append(Issue(issue.title, issue.body, labels))

        return Issues(issues)

class CommitMapper(BaseMapper):

    def __init__(self) -> None:
        super().__init__('CommitMapper', [], memoize=False)
        self.__cache = LRUCache(64)

    def _generate_mapped_data_point(self, x: DataPoint) -> Optional[DataPoint]:
        key = (x.owner, x.repository, x.sha)
        if key in self.__cache: return self.__cache[key]

        commit = Commit(x.owner, x.repository, x.sha, x.message)
        self.__cache[key] = commit

        return commit

class commit_lf(labeling_function):
    def __init__(
        self,
        name: Optional[str] = None,
        resources: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(name, resources, pre=[CommitMapper()])