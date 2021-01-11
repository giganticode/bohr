from bohr.framework import DATA_DIR
from bohr.framework.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.framework.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "1151-commits",
    path_to_file=DATA_DIR / "bugginess" / "test" / "1151-commits.csv",
    mapper=CommitMapper(),
    test_set=True,
)
