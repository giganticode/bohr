from bohr import DATA_DIR
from bohr.datasets.templates.loaders.from_csv import CsvDatasetLoader
from bohr.datasets.templates.mappers.method import MethodMapper

dataset_loader = CsvDatasetLoader(
    "smells-train",
    path_to_file=DATA_DIR / "smells" / "train.csv",
    mapper=MethodMapper(),
    sep=";",
    test_set=False,
)
