from pathlib import Path
from typing import Optional

import pandas as pd

from bohr.core import DatasetLoader, ArtifactMapper
from bohr.datasets.templates.mappers.commit import CommitMapper


class CsvDatasetLoader(DatasetLoader):
    def __init__(
        self,
        name: str,
        path_to_file: Path,
        n_rows: Optional[int] = None,
        test_set: bool = False,
    ):
        super().__init__(name, test_set)
        self.path_to_file = path_to_file
        self.n_rows = n_rows

    def load(self) -> pd.DataFrame:
        artifact_df = pd.read_csv(self.path_to_file, nrows=self.n_rows)
        artifact_df.message = artifact_df.message.astype(str)
        return artifact_df

    def get_mapper(self) -> ArtifactMapper:
        return CommitMapper()
