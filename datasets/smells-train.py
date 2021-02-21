from bohr.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.templates.datamappers.method import MethodMapper

dataset_loader = CsvDatasetLoader(
    path_to_file="data/smells/train.csv",
    mapper=MethodMapper(),
    sep=";",
    test_set=False,
)

__all__ = [dataset_loader]
