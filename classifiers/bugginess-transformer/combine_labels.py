import sys
from pathlib import Path

import pandas as pd

from bohr.config.pathconfig import PathConfig


def combine_labels(path_to_labeled_dataset: Path, path_to_transformer_labels, output_path: Path) -> None:
    labeled_dataset = pd.read_csv(path_to_labeled_dataset)
    transformer_labels = pd.read_csv(path_to_transformer_labels)['prediction'].rename('transformer_preds')
    combined = pd.concat([labeled_dataset, transformer_labels], axis=1)
    combined.to_csv(output_path)


if __name__ == '__main__':
    project_root = PathConfig.load().project_root
    combine_labels(project_root / Path(sys.argv[1]),
                   project_root / Path(sys.argv[2]),
                   project_root / Path(sys.argv[3]))