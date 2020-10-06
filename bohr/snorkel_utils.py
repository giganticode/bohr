from functools import wraps, cached_property, lru_cache
from typing import Optional, List, Set, Mapping, Any, Tuple, Callable, Union
from snorkel.types import DataPoint

from bohr import TEST_DIR, TRAIN_DIR

from dataclasses import dataclass, field
from cachetools import LRUCache

import pandas as pd

import snorkel
from snorkel.labeling import labeling_function, LabelingFunction
from snorkel.preprocess import preprocessor, BasePreprocessor
from snorkel.map import BaseMapper, LambdaMapper
from snorkel.map.core import MapFunction

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer 
from nltk import bigrams

Label = int

BUG = 1
BUGLESS = 0
ABSTAIN = -1

LABEL_NAMES = {
    BUG: 'bug',
    BUGLESS: 'bugless',
}

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
    def ordered_stems(self) -> List[str]:
        stemmer = PorterStemmer()
        return [stemmer.stem(w) for w in self.tokens]

    @cached_property
    def stems(self) -> Set[str]:
        return set(self.ordered_stems)

    @cached_property
    def stem_bigrams(self) -> Set[Tuple[str, str]]:
        return set(bigrams(self.ordered_stems))



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

    def contains_label(self, stemmed_label: str) -> bool:
        for issue in self.__issues:
            if stemmed_label in issue.stemmed_labels: return True
        return False

    def match(self, stemmed_keywords: Set[str]) -> bool:
        for issue in self.__issues:
            if not issue.stems.isdisjoint(stemmed_keywords): return True
        return False

    def contains(self, stemmed_keyword: str) -> bool:
        for issue in self.__issues:
            if stemmed_keyword in issue.stems: return True
        return False

    def match_bigram(self, stemmed_bigrams: Set[Tuple[str, str]]) -> bool:
        for issue in self.__issues:
            if not issue.stem_bigrams.isdisjoint(stemmed_bigrams): return True
        return False

    def contains_bigram(self, stemmed_bigram: Tuple[str, str]) -> bool:
        for issue in self.__issues:
            if stemmed_bigram in issue.stem_bigrams: return True
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
    def ordered_stems(self) -> List[str]:
        stemmer = PorterStemmer()
        return [stemmer.stem(w) for w in self.tokens]

    @cached_property
    def stems(self) -> Set[str]:
        return set(self.ordered_stems)

    @cached_property
    def stem_bigrams(self) -> Set[Tuple[str, str]]:
        return set(bigrams(self.ordered_stems))

    def match(self, stemmed_keywords: Set[str]) -> bool:
        return not self.stems.isdisjoint(stemmed_keywords)

    def match_bigram(self, stemmed_bigrams: Set[Tuple[str, str]]) -> bool:
        return not self.stem_bigrams.isdisjoint(stemmed_bigrams)



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
            return pd.read_csv(path, index_col=['sha'], keep_default_na=False)
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
            try:
                df = df.loc[[self.sha]]
                for sha, issue in df.iterrows():
                    labels = issue.labels
                    labels = list(filter(None, labels.split(', ')))

                    issues.append(Issue(issue.title, issue.body, labels))
            except KeyError as e:
                pass

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
    def __call__(self, f: Callable[..., int]) -> LabelingFunction:
        name = self.name or f.__name__
        return CommitLabelingFunction(name=name, f=f, resources=self.resources, pre=self.pre)


def keywords_lookup_in_message(commit: Commit, keywords, bigrams, label):
    if keywords and commit.message.match(keywords): return label
    if bigrams and commit.message.match_bigram(bigrams): return label
    return ABSTAIN

def keywords_lookup_in_issue_label(commit: Commit, keywords, bigrams, label):
    if keywords and commit.issues.match_label(keywords): return label
    return ABSTAIN

def keywords_lookup_in_issue_body(commit: Commit, keywords, bigrams, label):
    if keywords and commit.issues.match(keywords): return label
    if bigrams and commit.issues.match_bigram(bigrams): return label
    return ABSTAIN

def keyword_lookup_in_message(commit: Commit, keyword, bigram, label):
    if keyword in commit.message.stems: return label
    if bigram in commit.message.stem_bigrams: return label
    return ABSTAIN

def keyword_lookup_in_issue_label(commit: Commit, keyword, bigram, label):
    if keyword and commit.issues.contains_label(keyword): return label
    return ABSTAIN

def keyword_lookup_in_issue_body(commit: Commit, keyword, bigram, label):
    if commit.issues.contains(keyword): return label
    if commit.issues.contains_bigram(bigram): return label
    return ABSTAIN

def keyword_lf(where: str, keywords: Union[str, Set[str]], label: Label, bigrams: Union[Tuple[str, str], Set[Tuple[str, str]]] = None):

    name_elem = None
    label_name = LABEL_NAMES[label]
    multi = False
    
    if isinstance(keywords, str):
        name_elem = keywords
    elif isinstance(keywords, set):
        name_elem = next(iter(keywords))
        multi = True

    if isinstance(bigrams, tuple):
        name_elem = name_elem or ' '.join(bigrams)
    if isinstance(bigrams, set):
        name_elem = name_elem or ' '.join(next(iter(bigrams)))
        multi = True

    keyword_or_bigram_str = f"{'keyword' if keywords is not None else 'bigram'}{'s' if multi else ''}"

    name = f"{label_name}_{where}_{keyword_or_bigram_str}_{name_elem}"

    if multi:
        resources = dict(keywords=keywords, bigrams=bigrams, label=label)
    else:
        resources = dict(keyword=keywords, bigram=bigrams, label=label)

    return CommitLabelingFunction(
        name=name,
        f=globals()[f"keyword{'s' if multi else ''}_lookup_in_{where}"],
        resources=resources
    )

def keyword_lfs(keywords: List[str], where: str, label: Label):
    lfs = []
    for elem in keywords:
        if isinstance(elem, str):
            if ' ' in elem:
                lfs.append(keyword_lf(where, keywords=None, bigrams=tuple(elem.split(' ')), label=label))
            else:
                lfs.append(keyword_lf(where, elem, label))
        elif isinstance(elem, list):
            keywords = []
            bigrams = []

            for kw in elem:
                if ' ' in kw:
                    bigrams.append(tuple(kw.split(' ')))
                else:
                    keywords.append(kw)                    

            lfs.append(keyword_lf(where, keywords=set(keywords) if keywords else None,
                                         bigrams=set(bigrams) if bigrams else None, label=label))
        else:
            raise ValueError()                

    return lfs
