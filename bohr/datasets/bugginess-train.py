from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader
from bohr.datasets.templates.mappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "bugginess-train",
    path_to_file=DATA_DIR / "train" / "bug_sample.csv",
    mapper=CommitMapper(),
    test_set=False,
)
