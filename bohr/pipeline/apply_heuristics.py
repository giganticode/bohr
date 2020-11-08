import json
from pathlib import Path
from pprint import pprint, pformat
from typing import Any, Dict, List

import dask.dataframe as dd
import numpy as np
import pandas as pd
from dask.diagnostics import ProgressBar
from numpyencoder import NumpyEncoder
from snorkel.labeling import PandasLFApplier, LFAnalysis
from snorkel.labeling.apply.dask import PandasParallelLFApplier
from snorkel.labeling.model import MajorityLabelVoter

from bohr import PROJECT_DIR, TEST_DIR, params
from bohr.core import load_labeling_functions


def majority_acc(L: np.ndarray, df: dd.DataFrame) -> float:
    majority_model = MajorityLabelVoter()
    maj_model_train_acc = majority_model.score(L=L, Y=df.bug, tie_break_policy="random")["accuracy"]
    return maj_model_train_acc


def apply_lfs_to_train_set(lfs: List, save_generated_to: Path, save_metrics_to: Path) -> Dict[str, Any]:
    commit_df = pd.read_csv(params.COMMITS_FILE, nrows=params.N_ROWS)

    commit_df.message = commit_df.message.astype(str)

    if params.N_PARALLEL <= 1:
        applier = PandasLFApplier(lfs=lfs)
        applied_lf_matrix = applier.apply(df=commit_df)
    else:
        ProgressBar().register()
        applier = PandasParallelLFApplier(lfs=lfs)
        applied_lf_matrix = applier.apply(df=commit_df, n_parallel=params.N_PARALLEL)

    applied_lf_matrix.dump(save_generated_to / 'heuristic_matrix_train.pkl')

    lf_analysis_summary = LFAnalysis(applied_lf_matrix, lfs).lf_summary()
    lf_analysis_summary.to_csv(save_generated_to / 'analysis_train.csv')
    analysis_dict = lf_analysis_summary.to_dict()
    del analysis_dict['j']
    with open(save_metrics_to / 'analysis_train.json', 'w') as f:
        json.dump(analysis_dict, f, indent=4, sort_keys=True, cls=NumpyEncoder)
    coverage_train = sum((applied_lf_matrix != -1).any(axis=1)) / len(applied_lf_matrix)
    return {'n_labeling_functions': len(lfs), 'coverage_train': coverage_train}


def apply_lfs_to_test_set(lfs: List, test_set: str, save_generated_to: Path, save_metrics_to: Path) -> Dict[str, float]:
    applier = PandasLFApplier(lfs=lfs)
    df = pd.read_csv(TEST_DIR / f'{test_set}.csv')
    L = applier.apply(df=df)
    L.dump(save_generated_to / f'heuristic_matrix_{test_set}.pkl')
    lf_analysis_summary = LFAnalysis(L, lfs).lf_summary(Y=df.bug.values)
    lf_analysis_summary.to_csv(save_generated_to / f'analysis_{test_set}.csv')
    analysis_dict = lf_analysis_summary.to_dict()
    del analysis_dict['j']
    with open(save_metrics_to / f'analysis_{test_set}.json', 'w') as f:
        json.dump(analysis_dict, f, indent=4, sort_keys=True, cls=NumpyEncoder)
    coverage = sum((L != -1).any(axis=1)) / len(L)
    majority_accuracy = majority_acc(L, df)
    return {f'coverage_{test_set}': coverage, f'majority_accuracy_{test_set}': majority_accuracy}


def apply_heuristics(task: str) -> None:
    all_stats: Dict[str, Any] = {}

    task_dir_generated = PROJECT_DIR / 'generated' / task
    task_dir_metrics = PROJECT_DIR / 'metrics' / task
    if not task_dir_generated.exists():
        task_dir_generated.mkdir(parents=True)
    if not task_dir_metrics.exists():
        task_dir_metrics.mkdir(parents=True)

    lfs = load_labeling_functions({task})
    stats = apply_lfs_to_train_set(lfs, save_generated_to=task_dir_generated, save_metrics_to=task_dir_metrics)
    all_stats.update(**stats)

    for test_set in params.TEST_SETS:
        stats = apply_lfs_to_test_set(lfs, test_set,
                                      save_generated_to=task_dir_generated, save_metrics_to=task_dir_metrics)
        all_stats.update(**stats)

    with open(task_dir_metrics / 'heuristic_metrics.json', 'w') as f:
        json.dump(all_stats, f)

    pprint(all_stats)


class Profiler(object):
    def __init__(self, enabled: bool):
        self.enabled = enabled
        if self.enabled:
            import cProfile
            self.profiler = cProfile.Profile()

    def __enter__(self):
        if self.enabled:
            self.profiler.enable()

    def __exit__(self, type, value, traceback):
        if self.enabled:
            self.profiler.disable()
            self.profiler.print_stats(sort='cumtime')


if __name__ == '__main__':
    with Profiler(enabled=params.PROFILE):
        apply_heuristics(params.TASK)
