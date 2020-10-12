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

    df_herzig = pd.read_csv(TEST_DIR / 'herzig.csv')
    df_berger = pd.read_csv(TEST_DIR / 'berger.csv')
    df_1151_commits = pd.read_csv(TEST_DIR / '1151-commits.csv')
    heuristic_groups = "_".join(args.heuristic_groups)
    L_train = np.load(PROJECT_DIR / 'generated' / heuristic_groups / args.path_to_heuristics_matrix_train, allow_pickle=True)
    L_herzig = np.load(PROJECT_DIR / 'generated' / heuristic_groups / args.path_to_heuristics_matrix_herzig, allow_pickle=True)
    L_berger = np.load(PROJECT_DIR / 'generated' / heuristic_groups / args.path_to_heuristics_matrix_berger, allow_pickle=True)
    L_1151_commits = np.load(PROJECT_DIR / 'generated' / heuristic_groups / args.path_to_heuristics_matrix_1151_commits, allow_pickle=True)

    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(L_train=L_train, n_epochs=100, log_freq=100, seed=123)
    label_model.save(PROJECT_DIR / 'generated' / heuristic_groups / args.save_label_model_to)
    label_model.eval()

    stats['label_model_acc_herzig'] = label_model.score(L=L_herzig, Y=df_herzig.bug, tie_break_policy="random")["accuracy"]
    stats['label_model_acc_berger'] = label_model.score(L=L_berger, Y=df_berger.bug, tie_break_policy="random")["accuracy"]
    stats['label_model_acc_1151_commits'] = label_model.score(L=L_1151_commits, Y=df_1151_commits.bug, tie_break_policy="random")["accuracy"]
    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('heuristic_groups', nargs='+')
    parser.add_argument('--path-to-heuristics-matrix-train', default='heuristic_matrix_train.pkl')
    parser.add_argument('--path-to-heuristics-matrix-herzig', default='heuristic_matrix_herzig.pkl')
    parser.add_argument('--path-to-heuristics-matrix-berger', default='heuristic_matrix_berger.pkl')
    parser.add_argument('--path-to-heuristics-matrix-1151-commits', default='heuristic_matrix_1151_commits.pkl')
    parser.add_argument('--save-label-model-to', default='label_model.pkl')
    parser.add_argument('--save-metrics-to', default='label_model_metrics.json')
    args = parser.parse_args()

    stats = train_label_model(args)
    heuristic_groups = "_".join(args.heuristic_groups)
    with open(PROJECT_DIR / 'metrics' / heuristic_groups / Path(args.save_metrics_to), 'w') as f:
        json.dump(stats, f)

    pprint(stats)
