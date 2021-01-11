from bohr.framework import DATA_DIR
from bohr.framework.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.framework.templates.datamappers.method import MethodMapper

dataset_loader = CsvDatasetLoader(
    "smells-train",
    path_to_file=DATA_DIR / "smells" / "train.csv",
    mapper=MethodMapper(),
    sep=";",
    test_set=False,
)
