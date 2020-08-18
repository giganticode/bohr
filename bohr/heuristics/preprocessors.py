from typing import Any, Callable, List
import pandas as pd

from snorkel.preprocess import preprocessor


@preprocessor()
def get_field_extractor(field: str) -> Callable[[pd.Series], Any]:
    def field_extractor(x: pd.Series) -> Any:
        return x[field]
    return field_extractor


@preprocessor()
def lowercase(x: str) -> str:
    return x.lower()


@preprocessor()
def tokenize(x: str) -> List[str]:
    return x.split(" ")
