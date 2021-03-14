from pathlib import Path

from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from datamappers.idans_commit import IdansCommitMapper

dataset_loader = CsvDatasetLoader(
    path_to_file="data/bugginess/train/plain_commits_batch1.csv",
    mapper=IdansCommitMapper(Path(__file__).parent.parent),
    test_set=True,
)

__all__ = [dataset_loader]
