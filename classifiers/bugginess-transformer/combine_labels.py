import sys
from pathlib import Path

import pandas as pd

from bohr.pathconfig import load_path_config


def combine_labels(path_to_labeled_dataset: Path, path_to_transformer_labels, output_path: Path) -> None:
    labeled_dataset = pd.read_csv(path_to_labeled_dataset)
    transformer_labels = pd.read_csv(path_to_transformer_labels)['prediction'].rename('transformer_preds')
    combined = pd.concat([labeled_dataset, transformer_labels], axis=1)
    combined.to_csv(output_path)


if __name__ == '__main__':
    project_root = load_path_config().project_root
    combine_labels(project_root / Path(sys.argv[1]),
                   project_root / Path(sys.argv[2]),
                   project_root / Path(sys.argv[3]))