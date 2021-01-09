from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader
from bohr.datasets.templates.mappers.method import MethodMapper

dataset_loader = CsvDatasetLoader(
    "smells-test_10",
    path_to_file=DATA_DIR / "smells" / "test.csv",
    mapper=MethodMapper(),
    sep=";",
    n_rows=10,
    test_set=True,
)
