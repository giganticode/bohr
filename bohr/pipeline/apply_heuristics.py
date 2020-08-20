
import os
from pathlib import Path

import argparse
import json
from pprint import pprint
from typing import Any, Dict

import numpy as np
import pandas as pd
import dask.dataframe as dd
import csv

from snorkel.labeling import PandasLFApplier
from snorkel.labeling.apply.dask import DaskLFApplier, PandasParallelLFApplier

from snorkel.labeling.model import MajorityLabelVoter

from bohr.heuristics import all_lfs
import bohr.heuristics.bug as bug_heuristics
from bohr.snorkel_utils import BUG, BUGLESS
from bohr import PROJECT_DIR, TRAIN_DIR, TEST_DIR

def majority_acc(L: np.ndarray, df: dd.DataFrame) -> float:
    majority_model = MajorityLabelVoter()
    maj_model_train_acc = majority_model.score(L=L, Y=df.bug, tie_break_policy="random")["accuracy"]
    return maj_model_train_acc

def apply_heuristics(args) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}

    df_train = pd.read_csv(TRAIN_DIR / 'b_b.csv', nrows=args.rows_train)
    df_test = pd.concat([pd.read_csv(p) for p in TEST_DIR.glob('*.csv')], ignore_index=True)

    df_train.message = df_train.message.astype(str)

    lfs = all_lfs(bug_heuristics)

    stats['n_labeling_functions'] = len(lfs)

    applier = PandasParallelLFApplier(lfs=lfs)
    L_dev = applier.apply(df=df_train, n_parallel=6)
    L_dev.dump(PROJECT_DIR / args.save_heuristics_matrix_train_to)

    applier = PandasParallelLFApplier(lfs=lfs)
    L_test = applier.apply(df=df_test, n_parallel=6)
    L_test.dump(PROJECT_DIR / args.save_heuristics_matrix_test_to)

    stats['coverage_train'] = sum((L_dev != -1).any(axis=1)) / len(L_dev)
    stats['coverage_test'] = sum((L_test != -1).any(axis=1)) / len(L_test)

    # stats['majority_accuracy_train'] = majority_acc(L_dev, df_train)
    stats['majority_accuracy_test'] = majority_acc(L_test, df_test)

    return stats

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows-train', type=int, default=50000)
    parser.add_argument('--rows-test', type=int, default=5000)
    parser.add_argument('--save-heuristics-matrix-train-to', default='generated/heuristic_matrix_train.pkl')
    parser.add_argument('--save-heuristics-matrix-test-to', default='generated/heuristic_matrix_test.pkl')
    parser.add_argument('--save-metrics-to', default='heuristic_metrics.json')
    args = parser.parse_args()

    stats = apply_heuristics(args)

    with open(PROJECT_DIR / Path(args.save_metrics_to), 'w') as f:
        json.dump(stats, f)

    pprint(stats)