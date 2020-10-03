from pathlib import Path
import os

import argparse
import json
from pprint import pprint
from typing import Any, Dict
import pandas as pd
import numpy as np

from bohr import PROJECT_DIR, TRAIN_DIR, TEST_DIR

from snorkel.labeling.model import LabelModel


def train_label_model(args) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}

    train_filename = TRAIN_DIR / 'b_b.csv'

    df_train = pd.read_csv(train_filename,  sep=',', index_col=0, nrows=50000)
    df_test = df_test = pd.concat([pd.read_csv(p)
                                   for p in TEST_DIR.glob('*.csv')], ignore_index=True, sort=True)

    L_dev = np.load(PROJECT_DIR / args.path_to_heuristics_matrix_train, allow_pickle=True)
    L_test = np.load(PROJECT_DIR / args.path_to_heuristics_matrix_test, allow_pickle=True)

    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(L_train=L_dev, n_epochs=150, log_freq=100, seed=123)
    label_model.save(PROJECT_DIR / args.save_label_model_to)
    label_model.eval()
    # stats['label_model_train_acc'] = label_model.score(L=L_dev, Y=df_train.label, tie_break_policy="random")["accuracy"]
    stats['label_model_test_acc'] = label_model.score(L=L_test, Y=df_test.bug, tie_break_policy="random")["accuracy"]
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path-to-heuristics-matrix-train', default='generated/heuristic_matrix_train.pkl')
    parser.add_argument('--path-to-heuristics-matrix-test', default='generated/heuristic_matrix_test.pkl')
    parser.add_argument('--save-label-model-to', default='generated/label_model.pkl')
    parser.add_argument('--save-metrics-to', default='label_model_metrics.json')
    args = parser.parse_args()

    stats = train_label_model(args)

    with open(PROJECT_DIR / Path(args.save_metrics_to), 'w') as f:
        json.dump(stats, f)

    pprint(stats)
