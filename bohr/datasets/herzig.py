from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader


dataset_loader = CsvDatasetLoader(
    "herzig", path_to_file=DATA_DIR / "test" / "herzig.csv", test_set=True
)
