from bohr.framework import DATA_DIR
from bohr.framework.templates.dataloaders.from_csv import CsvDatasetLoader
from bohr.framework.templates.datamappers.commit import CommitMapper

dataset_loader = CsvDatasetLoader(
    "bugginess-train-10k",
    path_to_file=DATA_DIR / "bugginess" / "train" / "bug_sample.csv",
    mapper=CommitMapper(),
    n_rows=10000,
    test_set=False,
    additional_data_files=[
        DATA_DIR / "bugginess" / "train" / "bug_sample_issues.csv",
        DATA_DIR / "bugginess" / "train" / "bug_sample_files.csv",
    ],
)
