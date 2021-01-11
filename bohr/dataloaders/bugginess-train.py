from bohr.framework import DATA_DIR
from bohr.framework.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.framework.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "bugginess-train",
    path_to_file=DATA_DIR / "bugginess" / "train" / "bug_sample.csv",
    mapper=CommitMapper(),
    test_set=False,
)
