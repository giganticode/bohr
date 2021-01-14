import functools
import importlib
import inspect
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Set, Type

from dask.dataframe import DataFrame
from snorkel.map import BaseMapper

from bohr.framework import (
    ARTIFACT_PACKAGE,
    DATASET_DIR,
    DATASET_PACKAGE,
    HEURISTIC_DIR,
    HEURISTIC_PACKAGE,
    TASK_DIR,
    TASK_PACKAGE,
)
from bohr.framework.artifacts.core import Artifact
from bohr.framework.labels.cache import CategoryMappingCache
from bohr.framework.labels.labelset import Label
from bohr.framework.snorkel_util import SnorkelLabelingFunction, to_snorkel_label

KEYWORD_GROUP_SEPARATOR = "|"


logger = logging.getLogger(__name__)


class ArtifactMapper(BaseMapper, ABC):
    @abstractmethod
    def get_artifact(self) -> Type:
        pass


class _Heuristic:
    def __init__(
        self, func: Callable, artifact_type_applied_to: Type[Artifact], resources=None
    ):
        self.artifact_type_applied_to = artifact_type_applied_to
        self.resources = resources
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, artifact: Artifact, *args, **kwargs) -> Label:
        return self.func(artifact, *args, **kwargs)


class Heuristic:
    def __init__(self, artifact_type_applied_to: Type[Artifact]):
        self.artifact_type_applied_to = artifact_type_applied_to

    def get_artifact_safe_func(self, f: Callable) -> Callable[..., Optional[Label]]:
        def func(artifact, *args, **kwargs):
            if not isinstance(artifact, self.artifact_type_applied_to):
                raise ValueError("Not right artifact")
            try:
                return f(artifact, *args, **kwargs)
            except (ValueError, KeyError, AttributeError, IndexError, TypeError):
                logger.exception(
                    "Exception thrown while applying heuristic, "
                    "skipping the heuristic for this datapoint ..."
                )
                return None

        return functools.wraps(f)(func)

    def __call__(self, f: Callable[..., Label]) -> _Heuristic:
        safe_func = self.get_artifact_safe_func(f)
        return _Heuristic(safe_func, self.artifact_type_applied_to)


def load_heuristics_from_module(
    artifact_type: Type, module_name: str
) -> List[_Heuristic]:
    def is_heuristic_of_needed_type(obj):
        return (
            isinstance(obj, _Heuristic)
            and obj.artifact_type_applied_to == artifact_type
        )

    heuristics: List[_Heuristic] = []
    module = importlib.import_module(f"{HEURISTIC_PACKAGE}.{module_name}")
    heuristics.extend(
        [
            obj
            for name, obj in inspect.getmembers(module)
            if is_heuristic_of_needed_type(obj)
        ]
    )
    for name, obj in inspect.getmembers(module):
        if (
            isinstance(obj, list)
            and len(obj) > 0
            and is_heuristic_of_needed_type(obj[0])
        ):
            heuristics.extend(obj)
    return heuristics


def check_names_unique(heuristics: List[_Heuristic]) -> None:
    name_set = set()
    for heuristic in heuristics:
        name = heuristic.func.__name__
        if name in name_set:
            raise ValueError(f"Heuristic with name {name} already exists.")
        name_set.add(name)


def load_heuristics(
    artifact_type: Type, limited_to_modules: Optional[Set[str]] = None
) -> List[_Heuristic]:
    heuristics: List[_Heuristic] = []
    for heuristic_file in next(os.walk(HEURISTIC_DIR))[2]:
        heuristic_module_name = ".".join(heuristic_file.split(".")[:-1])
        if limited_to_modules is None or heuristic_module_name in limited_to_modules:
            heuristics.extend(
                load_heuristics_from_module(artifact_type, heuristic_module_name)
            )
    check_names_unique(heuristics)
    return heuristics


@dataclass
class DatasetLoader(ABC):
    name: str
    test_set: bool
    mapper: ArtifactMapper

    def get_artifact(self) -> Type:
        return self.get_mapper().get_artifact()

    @abstractmethod
    def load(self) -> DataFrame:
        pass

    @abstractmethod
    def get_paths(self) -> List[Path]:
        pass

    def get_mapper(self) -> ArtifactMapper:
        return self.mapper

    def is_test_set(self):
        return self.test_set


def get_dataset_loader(name: str) -> DatasetLoader:
    try:
        module = importlib.import_module(f"{DATASET_PACKAGE}.{name}")
        obj = getattr(module, "dataset_loader")
        return obj
    except AttributeError as e:
        raise ValueError("The dataset loader is defined incorrectly.") from e
    except ModuleNotFoundError as e:
        raise ValueError(f"Dataset {name} not defined.") from e


def get_all_dataset_loaders() -> Set:
    res = set()
    for dataset_file in next(os.walk(DATASET_DIR))[2]:
        dataset_name = ".".join(dataset_file.split(".")[:-1])
        try:
            loader = get_dataset_loader(dataset_name)
            res.add(loader)
        except ValueError:
            pass
    return res


def apply_heuristic_and_convert_to_snorkel_label(
    heuristic: _Heuristic, cache: CategoryMappingCache, *args, **kwargs
) -> int:
    return to_snorkel_label(heuristic(*args, **kwargs), cache)


def to_labeling_functions(
    heuristics: List[_Heuristic], mapper: ArtifactMapper, labels: List[str]
) -> List[SnorkelLabelingFunction]:
    category_mapping_cache = CategoryMappingCache(labels, maxsize=10000)
    labeling_functions = list(
        map(
            lambda x: SnorkelLabelingFunction(
                name=f"{x[1].__name__}_{x[0]}",
                f=lambda *args, **kwargs: apply_heuristic_and_convert_to_snorkel_label(
                    x[1], category_mapping_cache, *args, **kwargs
                ),
                mapper=mapper,
                resources=x[1].resources,
            ),
            enumerate(heuristics),
        )
    )
    return labeling_functions


@dataclass
class Task:
    name: str
    top_artifact: Type
    labels: List[str]
    train_datasets: List[DatasetLoader]
    test_datasets: List[DatasetLoader]
    label_column_name: str

    @property
    def datasets(self) -> List[DatasetLoader]:
        return self.train_datasets + self.test_datasets

    def _datapaths(self, datasets: List[DatasetLoader]) -> List[Path]:
        return [p for dataset in datasets for p in dataset.get_paths()]

    @property
    def datapaths(self) -> List[Path]:
        return self.train_datapaths + self.test_datapaths

    @property
    def train_datapaths(self) -> List[Path]:
        return self._datapaths(self.train_datasets)

    @property
    def test_datapaths(self) -> List[Path]:
        return self._datapaths(self.test_datasets)

    def __post_init__(self):
        for test_dataset in self.train_datasets + self.test_datasets:
            if test_dataset.get_artifact() != self.top_artifact:
                raise ValueError(
                    f"Dataset {test_dataset} is a dataset of {test_dataset.get_artifact()}, "
                    f"but this task works on {self.top_artifact}"
                )

    @classmethod
    def load(cls, name: str) -> "Task":
        try:
            module = importlib.import_module(f"{TASK_PACKAGE}.{name}")
            top_artifact_str = getattr(module, "top_artifact")
            top_artifact = load_artifact_by_name(top_artifact_str)
            label_categories = getattr(module, "label_categories")
            test_dataset_names = getattr(module, "test_datasets")
            test_datasets = list(map(get_dataset_loader, test_dataset_names))
            try:
                train_dataset_names = getattr(module, "train_datasets")
                train_datasets = list(map(get_dataset_loader, train_dataset_names))
            except AttributeError:
                all_dataset_loaders = get_dataset_loaders(top_artifact)
                train_datasets = list(
                    filter(
                        lambda d: d.name not in test_dataset_names, all_dataset_loaders
                    )
                )
            try:
                label_column_name = getattr(module, "label_column_name")
            except AttributeError:
                label_column_name = name
            return cls(
                name,
                top_artifact,
                label_categories,
                train_datasets=train_datasets,
                test_datasets=test_datasets,
                label_column_name=label_column_name,
            )
        except AttributeError as e:
            raise ValueError("The task is defined incorrectly.") from e
        except ModuleNotFoundError as e:
            raise ValueError(f"Task {name} not defined.") from e


def load_artifact_by_name(artifact_name: str) -> Type:
    *path, name = artifact_name.split(".")
    try:
        module = importlib.import_module(f"{ARTIFACT_PACKAGE}.{'.'.join(path)}")
    except ModuleNotFoundError as e:
        raise ValueError(f'Module {".".join(path)} not defined.') from e

    try:
        artifact_type = getattr(module, name)
        return artifact_type
    except AttributeError as e:
        raise ValueError(f"Artifact {name} not found in module {module}") from e


def load_all_tasks() -> List[Task]:
    res = []
    for file in next(os.walk(TASK_DIR))[2]:
        task_name = ".".join(file.split(".")[:-1])
        try:
            task = Task.load(task_name)
            res.append(task)
        except ValueError:
            pass
    res = sorted(res, key=lambda x: x.name)
    return res


def get_dataset_loaders(artifact_type: Type) -> Set[DatasetLoader]:
    return set(
        filter(
            lambda d: d.get_mapper().get_artifact() == artifact_type,
            get_all_dataset_loaders(),
        )
    )
