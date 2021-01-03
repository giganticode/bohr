from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader
from bohr.datasets.templates.mappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "berger",
    path_to_file=DATA_DIR / "test" / "berger.csv",
    mapper=CommitMapper(),
    test_set=True,
)
