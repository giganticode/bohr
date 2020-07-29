
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
from snorkel.labeling.apply.dask import DaskLFApplier

from snorkel.labeling.model import MajorityLabelVoter

from bohr.heuristics.bugs import bugs, nonbugs
from bohr.snorkel_utils import BUG, BUGLESS
from bohr import PROJECT_DIR

def clean_text_columns(df: dd.DataFrame):
    for column in ["commit_message_stemmed", "issue_contents_stemmed"]:
        df[column].replace({'\n': ' '}, inplace=True, regex=True)
        df[column].replace({'\r': ' '}, inplace=True, regex=True)
        df[column].replace({'-': ' '}, inplace=True, regex=True) # jira regex does not work anymore with this preprocessing step
        df[column].replace({'/': ' '}, inplace=True, regex=True)
        df[column].replace({'_': ' '}, inplace=True, regex=True)
        df[column].replace({'\*': ' '}, inplace=True, regex=True)
        df[column].replace({r'\\': ' '}, inplace=True, regex=True)
        df[column].replace({'    ': ' '}, inplace=True, regex=True)
        df[column].replace({'"': ''}, inplace=True, regex=True)
        df[column].replace({'\'': ''}, inplace=True, regex=True)
        punctuation_signs = list("?:!.,;")
        for punct_sign in punctuation_signs:
            df[column] = df[column].str.replace(punct_sign, '')
        df.replace(np.nan, '', inplace=True, regex=True)


def majority_acc(L: np.ndarray, df: dd.DataFrame) -> float:
    majority_model = MajorityLabelVoter()
    maj_model_train_acc = majority_model.score(L=L, Y=df.label, tie_break_policy="random")["accuracy"]
    return maj_model_train_acc


def apply_heuristics(args) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}
    train_filename = PROJECT_DIR / args.dataset_path_train
    test_filename = PROJECT_DIR / args.dataset_path_test

    text_cols = ['Unnamed: 0', 'dataset', 'owner', 'repository', 'commit_id',
            'commit_message', 'commit_message_stemmed', 'issue_identifiers',
            'issue_contents', 'issue_contents_stemmed', 'issue_labels',
            'issue_labels_stemmed', 'code_changes', 'file_details']

    dtype = {c: 'object' for c in text_cols}
    dtype.update({'label': 'float64'})

    df_train = dd.read_csv(train_filename, dtype=dtype).set_index('Unnamed: 0').head(args.rows_train)
    df_test = dd.read_csv(test_filename, dtype=dtype,quoting=csv.QUOTE_MINIMAL ).set_index('Unnamed: 0').head(args.rows_test)

    stats['commits_train'] = len(df_train.index)
    stats['bugs_fraction'] = (df_train.label.values == BUG).mean()
    stats['nonbugs_fraction'] = (df_train.label.values == BUGLESS).mean()

    clean_text_columns(df_train)
    clean_text_columns(df_test)

    lfs = bugs.heuristics + nonbugs.heuristics

    stats['n_labeling_functions'] = len(lfs)

    applier = DaskLFApplier(lfs=lfs)
    L_dev = applier.apply(df=df_train)
    L_dev.dump(PROJECT_DIR / args.save_heuristics_matrix_train_to)

    applier = DaskLFApplier(lfs=lfs)
    L_test = applier.apply(df=df_test)
    L_test.dump(PROJECT_DIR / args.save_heuristics_matrix_test_to)

    stats['coverage_train'] = sum((L_dev != -1).any(axis=1)) / len(L_dev)
    stats['coverage_test'] = sum((L_test != -1).any(axis=1)) / len(L_test)

    stats['majority_accuracy_train'] = majority_acc(L_dev, df_train)
    stats['majority_accuracy_test'] = majority_acc(L_test, df_test)

    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-path-train', default = 'data/combination/Training_Dataset.csv')
    parser.add_argument('--dataset-path-test', default = 'data/combination/Test_Dataset.csv')
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