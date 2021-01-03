import argparse

import numpy as np
import pandas as pd
from snorkel.labeling.model import LabelModel

from bohr import PROJECT_DIR, LABELED_DATA_DIR
from bohr.core import (
    load_heuristics,
    DatasetLoader,
    Task,
    to_labeling_functions,
    get_dataset_loader,
)


def label_dataset(task_name: str, dataset_name: str, debug: bool = False):
    task = Task.load(task_name)
    dataset_loader = get_dataset_loader(dataset_name)
    df = dataset_loader.load()

    L_train = np.load(
        PROJECT_DIR / "generated" / task.name / "heuristic_matrix_train.pkl",
        allow_pickle=True,
    )

    print(L_train.shape)
    print(df.shape)

    heuristics = load_heuristics(task.top_artifact)
    labeling_functions = to_labeling_functions(
        heuristics, dataset_loader.get_mapper(), task.labels
    )

    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(L_train=L_train, n_epochs=100, log_freq=100, seed=123)

    labels, probs = label_model.predict(L=L_train, return_probs=True)
    df_labeled = df.assign(bug=labels)

    df_probs = pd.DataFrame(probs, columns=["prob_bugless", "prob_bug"])
    df_labeled = pd.concat([df_labeled, df_probs], axis=1)

    if debug:
        df_lfs = pd.DataFrame(L_train, columns=[lf.name for lf in labeling_functions])
        for name, col in df_lfs.iteritems():
            df_lfs[name] = col.map({0: name, 1: name, -1: ""})
        col_lfs = df_lfs.apply(lambda c: ";".join([v for v in c if v]), axis=1)
        df_labeled["lfs"] = col_lfs

    if not LABELED_DATA_DIR.exists():
        LABELED_DATA_DIR.mkdir(parents=True)
    df_labeled.to_csv(LABELED_DATA_DIR / dataset_name, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("dataset")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    label_dataset(args.task, args.dataset)
