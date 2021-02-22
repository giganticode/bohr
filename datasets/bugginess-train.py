from pathlib import Path

from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    path_to_file="data/bugginess/train/bug_sample.csv",
    mapper=CommitMapper(Path(__file__).parent.parent),
    test_set=False,
    additional_data_files=[
        "data/bugginess/train/bug_sample_issues.csv",
        "data/bugginess/train/bug_sample_files.csv",
    ],
)

__all__ = [dataset_loader]
