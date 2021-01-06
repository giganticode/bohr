from dataclasses import dataclass
from functools import cached_property
from typing import List, Set

from nltk import PorterStemmer, bigrams

from bohr.artifacts.core import Artifact
from bohr.nlp_utils import NgramSet, safe_tokenize


@dataclass
class CommitMessage(Artifact):
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
