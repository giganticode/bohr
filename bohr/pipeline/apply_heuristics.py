import argparse
import json
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, List, Tuple

import numpy as np
from dask.dataframe import DataFrame
from dask.diagnostics import ProgressBar
from numpyencoder import NumpyEncoder
from snorkel.labeling import LFAnalysis, PandasLFApplier
from snorkel.labeling.apply.dask import PandasParallelLFApplier
from snorkel.labeling.model import MajorityLabelVoter

from bohr import PROJECT_DIR
from bohr.core import Task, load_heuristics, to_labeling_functions
from bohr.pipeline.profiler import Profiler


def majority_acc(line: np.ndarray, df: DataFrame) -> float:
    majority_model = MajorityLabelVoter()
    maj_model_train_acc = majority_model.score(
        L=line, Y=df.bug, tie_break_policy="random"
    )["accuracy"]
    return maj_model_train_acc


def apply_lfs_to_train_set(
    lfs: List,
    artifact_df: DataFrame,
    save_generated_to: Path,
    save_metrics_to: Path,
    n_parallel: int,
) -> Dict[str, Any]:
    if n_parallel <= 1:
        applier = PandasLFApplier(lfs=lfs)
        applied_lf_matrix = applier.apply(df=artifact_df)
    else:
        ProgressBar().register()
        applier = PandasParallelLFApplier(lfs=lfs)
        applied_lf_matrix = applier.apply(df=artifact_df, n_parallel=n_parallel)

    applied_lf_matrix.dump(save_generated_to / "heuristic_matrix_train.pkl")

    lf_analysis_summary = LFAnalysis(applied_lf_matrix, lfs).lf_summary()
    lf_analysis_summary.to_csv(save_generated_to / "analysis_train.csv")
    analysis_dict = lf_analysis_summary.to_dict()
    del analysis_dict["j"]
    with open(save_metrics_to / "analysis_train.json", "w") as f:
        json.dump(analysis_dict, f, indent=4, sort_keys=True, cls=NumpyEncoder)
    coverage_train = sum((applied_lf_matrix != -1).any(axis=1)) / len(applied_lf_matrix)
    return {"n_labeling_functions": len(lfs), "coverage_train": coverage_train}


def apply_lfs_to_test_set(
    lfs: List,
    artifact_df: DataFrame,
    test_set_name: str,
    save_generated_to: Path,
    save_metrics_to: Path,
) -> Dict[str, float]:
    applier = PandasLFApplier(lfs=lfs)

    lines = applier.apply(df=artifact_df)
    lines.dump(save_generated_to / f"heuristic_matrix_{test_set_name}.pkl")
    lf_analysis_summary = LFAnalysis(lines, lfs).lf_summary(Y=artifact_df.bug.values)
    lf_analysis_summary.to_csv(save_generated_to / f"analysis_{test_set_name}.csv")
    analysis_dict = lf_analysis_summary.to_dict()
    del analysis_dict["j"]
    with open(save_metrics_to / f"analysis_{test_set_name}.json", "w") as f:
        json.dump(analysis_dict, f, indent=4, sort_keys=True, cls=NumpyEncoder)
    coverage = sum((lines != -1).any(axis=1)) / len(lines)
    majority_accuracy = majority_acc(lines, artifact_df)
    return {
        f"coverage_{test_set_name}": coverage,
        f"majority_accuracy_{test_set_name}": majority_accuracy,
    }


def create_dirs_if_necessary(task: Task) -> Tuple[Path, Path]:
    task_dir_generated = PROJECT_DIR / "generated" / task.name
    task_dir_metrics = PROJECT_DIR / "metrics" / task.name
    for dir in [task_dir_generated, task_dir_metrics]:
        if not dir.exists():
            dir.mkdir(parents=True)
    return task_dir_generated, task_dir_metrics


def apply_heuristics(task_name: str, n_parallel: int) -> None:
    task = Task.load(task_name)
    all_stats: Dict[str, Any] = {}

    task_dir_generated, task_dir_metrics = create_dirs_if_necessary(task)
    heuristics = load_heuristics(task.top_artifact)
    if not heuristics:
        raise ValueError(f"Heuristics not found for artifact: {task.top_artifact}")
    for dataset_loader in task.train_datasets:
        labeling_functions = to_labeling_functions(
            heuristics, dataset_loader.get_mapper(), task.labels
        )
        stats = apply_lfs_to_train_set(
            labeling_functions,
            artifact_df=dataset_loader.load(),
            save_generated_to=task_dir_generated,
            save_metrics_to=task_dir_metrics,
            n_parallel=n_parallel,
        )
        all_stats.update(**stats)

    for dataset_loader in task.test_datasets:
        labeling_functions = to_labeling_functions(
            heuristics, dataset_loader.get_mapper(), task.labels
        )
        stats = apply_lfs_to_test_set(
            labeling_functions,
            artifact_df=dataset_loader.load(),
            test_set_name=dataset_loader.name,
            save_generated_to=task_dir_generated,
            save_metrics_to=task_dir_metrics,
        )
        all_stats.update(**stats)

    with open(task_dir_metrics / "heuristic_metrics.json", "w") as f:
        json.dump(all_stats, f)

    pprint(all_stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", default="bugginess")
    parser.add_argument("--n-workers", type=int, default=1)
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    with Profiler(enabled=args.profile):
        apply_heuristics(args.task, args.n_workers)
