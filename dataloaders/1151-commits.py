from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "1151-commits",
    path_to_file="data/bugginess/test/1151-commits.csv",
    mapper=CommitMapper(),
    test_set=True,
)
