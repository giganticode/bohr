from typing import Any, Set, Tuple, Union

import pandas as pd
from nltk.tokenize import RegexpTokenizer

NgramSet = Set[Union[Tuple[str], str]]

_tokenizer = RegexpTokenizer(r"[\s_\.,%#/\?!\-\'\"\)\(\]\[\:;]", gaps=True)


def safe_tokenize(text: Any) -> Set[str]:
    if text is None:
        return set()
    if pd.isna(text):
        return set()

    tokens = _tokenizer.tokenize(str(text).lower())
    return tokens
