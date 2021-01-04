from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader
from bohr.datasets.templates.mappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "1151-commits",
    path_to_file=DATA_DIR / "test" / "1151-commits.csv",
    mapper=CommitMapper(),
    test_set=True,
)
