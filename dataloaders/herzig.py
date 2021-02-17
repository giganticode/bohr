from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "herzig",
    path_to_file="data/bugginess/test/herzig.csv",
    mapper=CommitMapper(),
    test_set=True,
)
