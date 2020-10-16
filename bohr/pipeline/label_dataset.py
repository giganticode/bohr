from pathlib import Path
import os

import argparse
import json
from pprint import pprint
from typing import Any, Dict
import pandas as pd
import numpy as np

from bohr import PROJECT_DIR, TRAIN_DIR, TEST_DIR
from bohr.core import load_labeling_functions

from snorkel.labeling.model import LabelModel


def label_dataset(args):
    heuristic_groups = "_".join(args.heuristic_groups)
    df = pd.read_csv(args.commits_file)

    L_train = np.load(PROJECT_DIR / 'generated' / heuristic_groups / args.path_to_heuristics_matrix_train, allow_pickle=True)

    print(L_train.shape)
    print(df.shape)

    lfs = load_labeling_functions(args.heuristic_groups)

    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(L_train=L_train, n_epochs=100, log_freq=100, seed=123)

    labels, probs = label_model.predict(L=L_train, return_probs=True)
    df_labeled = df.assign(bug=labels)

    df_probs = pd.DataFrame(probs, columns=['prob_bugless', 'prob_bug'])
    df_labeled = pd.concat([df_labeled, df_probs], axis=1)

    if args.debug:
        df_lfs = pd.DataFrame(L_train, columns=[lf.name for lf in lfs])
        for name, col in df_lfs.iteritems():
            df_lfs[name] = col.map({0: name, 1: name, -1: ''})
        col_lfs = df_lfs.apply(lambda c: ';'.join([v for v in c if v]), axis=1)
        df_labeled['lfs'] = col_lfs

    df_labeled.to_csv(args.o, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('heuristic_groups', nargs='+')
    parser.add_argument('--commits-file', required=True)
    parser.add_argument('-o', required=True)
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('--path-to-heuristics-matrix-train', default='heuristic_matrix_train.pkl')
    args = parser.parse_args()

    label_dataset(args)