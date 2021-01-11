from bohr.framework import DATA_DIR
from bohr.framework.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.framework.templates.datamappers.method import MethodMapper

dataset_loader = CsvDatasetLoader(
    "smells-train_10",
    path_to_file=DATA_DIR / "smells" / "train.csv",
    mapper=MethodMapper(),
    sep=";",
    n_rows=10,
    test_set=False,
)
