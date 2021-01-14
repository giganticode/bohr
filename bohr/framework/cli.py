import subprocess

from click import group

from bohr.framework import PROJECT_DIR
from bohr.framework.pipeline.dvc import add_all_tasks_to_dvc_pipeline

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@group(context_settings=CONTEXT_SETTINGS)
def bohr():
    pass


@bohr.command()
def repro():
    add_all_tasks_to_dvc_pipeline()
    subprocess.run(["dvc", "repro"], cwd=PROJECT_DIR)


if __name__ == "__main__":
    bohr()
