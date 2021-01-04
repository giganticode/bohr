from pathlib import Path
from typing import Optional

import pandas as pd

from bohr.core import ArtifactMapper, DatasetLoader


class CsvDatasetLoader(DatasetLoader):
    def __init__(
        self,
        name: str,
        path_to_file: Path,
        mapper: ArtifactMapper,
        n_rows: Optional[int] = None,
        sep: str = ",",
        test_set: bool = False,
    ):
        super().__init__(name, test_set, mapper)
        self.path_to_file = path_to_file
        self.n_rows = n_rows
        self.sep = sep

    def load(self) -> pd.DataFrame:
        artifact_df = pd.read_csv(self.path_to_file, nrows=self.n_rows, sep=self.sep)
        return artifact_df
