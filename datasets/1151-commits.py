from pathlib import Path

from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    path_to_file="data/bugginess/test/1151-commits.csv",
    mapper=CommitMapper(Path(__file__).parent.parent),
    test_set=True,
)

__all__ = [dataset_loader]
