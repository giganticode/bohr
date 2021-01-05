import argparse
import json
from pathlib import Path
from pprint import pprint
from typing import Any, Dict

import numpy as np
import pandas as pd
from snorkel.labeling.model import LabelModel

from bohr import PROJECT_DIR, TEST_DIR
from bohr.core import DatasetLoader, Task


def get_test_set_accuracy(
    label_model: LabelModel,
    test_set: DatasetLoader,
    save_to: Path,
    label_column_name: str,
) -> float:
    df = pd.read_csv(TEST_DIR / f"{test_set}.csv")
    lines = np.load(
        str(save_to / f"heuristic_matrix_{test_set.name}.pkl"), allow_pickle=True
    )
    return label_model.score(
        L=lines, Y=df[label_column_name], tie_break_policy="random"
    )["accuracy"]


def train_label_model(task_name: str) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}

    task_dir_generated = PROJECT_DIR / "generated" / task_name

    lines_train = np.load(
        task_dir_generated / "heuristic_matrix_train.pkl", allow_pickle=True
    )
    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(lines_train, n_epochs=100, log_freq=100, seed=123)
    label_model.save(task_dir_generated / "label_model.pkl")
    label_model.eval()

    task = Task.load(task_name)
    for test_set in task.test_datasets:
        stats[f"label_model_acc_{test_set.name}"] = get_test_set_accuracy(
            label_model,
            test_set,
            save_to=task_dir_generated,
            label_column_name=task.label_column_name,
        )

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    args = parser.parse_args()

    stats = train_label_model(args.task)
    with open(
        PROJECT_DIR / "metrics" / args.task / "label_model_metrics.json", "w"
    ) as f:
        json.dump(stats, f)

    pprint(stats)
