import logging
import re
import subprocess
from typing import List

from jinja2 import Environment, PackageLoader, StrictUndefined

from bohr.framework import PROJECT_DIR
from bohr.framework.core import Task, load_all_tasks

logger = logging.getLogger(__name__)

TEMPLATES = [
    "apply_heuristics.template",
    "train_label_model.template",
    "label_dataset.template",
]


def get_dvc_command(task: Task, template_name: str, no_exec: bool = True) -> List[str]:
    env = Environment(
        loader=PackageLoader("bohr", "framework"), undefined=StrictUndefined
    )
    template = env.get_template(f"resources/dvc_command_templates/{template_name}")
    command = template.render(task=task)
    if no_exec:
        command = f"dvc run --no-exec --force {command}"
    command_array = list(filter(None, re.split("[\n ]", command)))
    return command_array


def add_all_tasks_to_dvc_pipeline() -> None:
    all_tasks = load_all_tasks()
    logger.info(
        f"Following tasks are added to the pipeline: {list(map(lambda x: x.name, all_tasks))}"
    )
    for task in all_tasks:
        for template in TEMPLATES:
            command = get_dvc_command(task, template, no_exec=True)
            logger.info(f"Running {command}")
            subprocess.run(command, cwd=PROJECT_DIR)


if __name__ == "__main__":
    add_all_tasks_to_dvc_pipeline()
