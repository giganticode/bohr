import argparse

import numpy as np
import pandas as pd
from snorkel.labeling.model import LabelModel

from bohr.framework import LABELED_DATA_DIR, PROJECT_DIR
from bohr.framework.core import (
    Task,
    get_dataset_loader,
    load_heuristics,
    to_labeling_functions,
)


def label_dataset(task_name: str, dataset_name: str, debug: bool = False):
    task = Task.load(task_name)
    dataset_loader = get_dataset_loader(dataset_name)
    df = dataset_loader.load()

    lines_train = np.load(
        PROJECT_DIR / "generated" / task.name / "heuristic_matrix_train.pkl",
        allow_pickle=True,
    )

    print(lines_train.shape)
    print(df.shape)

    heuristics = load_heuristics(task.top_artifact)
    labeling_functions = to_labeling_functions(
        heuristics, dataset_loader.get_mapper(), task.labels
    )

    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(lines_train, n_epochs=100, log_freq=100, seed=123)

    labels, probs = label_model.predict(L=lines_train, return_probs=True)
    df_labeled = df.assign(bug=labels)

    df_probs = pd.DataFrame(probs, columns=["prob_bugless", "prob_bug"])
    df_labeled = pd.concat([df_labeled, df_probs], axis=1)

    if debug:
        df_lfs = pd.DataFrame(
            lines_train, columns=[lf.name for lf in labeling_functions]
        )
        for name, col in df_lfs.iteritems():
            df_lfs[name] = col.map({0: name, 1: name, -1: ""})
        col_lfs = df_lfs.apply(lambda c: ";".join([v for v in c if v]), axis=1)
        df_labeled["lfs"] = col_lfs

    if not LABELED_DATA_DIR.exists():
        LABELED_DATA_DIR.mkdir(parents=True)
    target_file = LABELED_DATA_DIR / f"{dataset_name}.csv"
    df_labeled.to_csv(target_file, index=False)
    print(f"Labeled dataset has been written to {target_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("dataset")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    label_dataset(args.task, args.dataset)