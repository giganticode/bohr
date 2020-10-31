
import os
from pathlib import Path

import argparse
import json
from pprint import pprint
from typing import Any, Dict

import numpy as np
import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import csv

from snorkel.labeling import PandasLFApplier, LFAnalysis
from snorkel.labeling.apply.dask import DaskLFApplier, PandasParallelLFApplier

from snorkel.labeling.model import MajorityLabelVoter

from bohr.core import load_labeling_functions
from bohr import PROJECT_DIR, TRAIN_DIR, TEST_DIR


def majority_acc(L: np.ndarray, df: dd.DataFrame) -> float:
    majority_model = MajorityLabelVoter()
    maj_model_train_acc = majority_model.score(
        L=L, Y=df.bug, tie_break_policy="random")["accuracy"]
    return maj_model_train_acc

def apply_heuristics(args) -> Dict[str, Any]:
    stats: Dict[str, Any] = {}

    df_train = pd.read_csv(args.commits_file, nrows)
    df_herzig = pd.read_csv(TEST_DIR / 'herzig.csv')
    df_berger = pd.read_csv(TEST_DIR / 'berger.csv')
    df_1151_commits = pd.read_csv(TEST_DIR / '1151-commits.csv')

    df_train.message = df_train.message.astype(str)
    scenario_name = "_".join(args.heuristic_groups)
    lfs = load_labeling_functions(args.heuristic_groups)

    stats[f'n_labeling_functions'] = len(lfs)

    if not (PROJECT_DIR / 'generated' / scenario_name).exists():
        (PROJECT_DIR / 'generated' / scenario_name).mkdir(parents=True)

    if args.n_parallel <= 1:
        applier = PandasLFApplier(lfs=lfs)
        L_train = applier.apply(df=df_train)
    else:
        ProgressBar().register()
        applier = PandasParallelLFApplier(lfs=lfs)
        L_train = applier.apply(df=df_train, n_parallel=args.n_parallel)

    L_train.dump(PROJECT_DIR / 'generated' / scenario_name / args.save_heuristics_matrix_train_to)

    LFAnalysis(L_train, lfs).lf_summary().to_csv(
        PROJECT_DIR / 'generated' / scenario_name / 'analysis_train.csv')

    applier = PandasLFApplier(lfs=lfs)
    L_herzig = applier.apply(df=df_herzig)
    L_herzig.dump(PROJECT_DIR / 'generated' / scenario_name / args.save_heuristics_matrix_herzig_to)
    L_berger = applier.apply(df=df_berger)
    L_berger.dump(PROJECT_DIR / 'generated' / scenario_name / args.save_heuristics_matrix_berger_to)
    L_1151_commits = applier.apply(df=df_1151_commits)
    L_1151_commits.dump(PROJECT_DIR / 'generated' / scenario_name / args.save_heuristics_matrix_1151_commits_to)

    LFAnalysis(L_herzig, lfs).lf_summary(Y=df_herzig.bug.values).to_csv(
        PROJECT_DIR / 'generated' / scenario_name / 'analysis_herzig.csv')
    LFAnalysis(L_berger, lfs).lf_summary(Y=df_berger.bug.values).to_csv(
        PROJECT_DIR / 'generated' / scenario_name / 'analysis_berger.csv')
    LFAnalysis(L_1151_commits, lfs).lf_summary(Y=df_1151_commits.bug.values).to_csv(
        PROJECT_DIR / 'generated' / scenario_name / 'analysis_1151_commits.csv')

    stats['coverage_train'] = sum((L_train != -1).any(axis=1)) / len(L_train)
    stats['coverage_herzig'] = sum((L_herzig != -1).any(axis=1)) / len(L_herzig)
    stats['coverage_berger'] = sum((L_berger != -1).any(axis=1)) / len(L_berger)
    stats['coverage_1151_commits'] = sum((L_1151_commits != -1).any(axis=1)) / len(L_1151_commits)

    stats['majority_accuracy_herzig'] = majority_acc(L_herzig, df_herzig)
    stats['majority_accuracy_berger'] = majority_acc(L_berger, df_berger)
    stats['majority_accuracy_1151_commits'] = majority_acc(L_1151_commits, df_1151_commits)

    return stats



if __name__ == '__main__':
    from bohr.pipeline.args import parse_heuristic_args

    args = parse_heuristic_args()

    if args.profile:
        import cProfile
        pr = cProfile.Profile()

    try:
        if args.profile:
            pr.enable()
        stats = apply_heuristics(args)
    finally:
        if args.profile:
            pr.disable()
            pr.print_stats(sort='cumtime')

    scenario_name = "_".join(args.heuristic_groups)
    if not (PROJECT_DIR / 'metrics' / scenario_name).exists():
        (PROJECT_DIR / 'metrics' / scenario_name).mkdir(parents=True)
    with open(PROJECT_DIR / 'metrics' / scenario_name / Path(args.save_metrics_to), 'w') as f:
        json.dump(stats, f)

    pprint(stats)
