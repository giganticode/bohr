from pathlib import Path

from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from datamappers.idans_commit import IdansCommitMapper

dataset_loader = CsvDatasetLoader(
    path_to_file="data/bugginess/test/plain_commits_batch_1m_test_labels.csv",
    mapper=IdansCommitMapper(Path(__file__).parent.parent),
    test_set=True,
)

__all__ = [dataset_loader]
