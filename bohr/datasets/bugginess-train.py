from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader

dataset_loader = CsvDatasetLoader(
    "bugginess-train",
    path_to_file=DATA_DIR / "train" / "bug_sample.csv",
    test_set=False,
)
