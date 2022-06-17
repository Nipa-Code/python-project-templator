import argparse
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import typing

from loguru import logger

aliases = {"gs": "git status", "gl": "git log --oneline"}  # not existing

GIT_PATH = r'"c:\Program Files\Git\bin\git.exe"'
GIT_TEMPLATE_URL = "https://github.com/Nipa-Code/python-project-template.git"

"""
NOTE: Add logoru, isort, black, flake8 + (config), requests
NOTE: python-decouple (.env),  to poetry to be installed in every build.
NOTE: Missing to Configure pre-commit hooks as well.
"""


def read_user_args(args: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Used to config the name of the project and possibly other stuff."
    )
    parser.add_argument(
        "-n",
        "--name",
        action="store",
        default="new_project",
        required=False,
        help="The name of new project.",
    )

    parser.add_argument(
        "-e",
        "--allow-only-empty",
        action="store_true",
        default=True,
        required=False,
        help="If True, will not create folders if directory is not empty.",
    )

    parser.add_argument(
        "-u",
        "--url",
        action="store",
        default=GIT_TEMPLATE_URL,
        required=False,
        help="The url of the template to clone. By default using some template of mine.",
    )

    return parser.parse_args(args)


def add_alias(name: str = None, command: str = None):
    """
    Add new alias to windows powershell to execute commands with simple shortcuts.
    :param name: The name of new alias.
    :param command: The command to execute.
    """
    if name is not None and command is not None:
        logger.info(f"adding alias {name} to {command}")
        subprocess.run(f"New-Alias {name} '{command}'", shell=True, capture_output=True)
        aliases[name] = command


def del_even_readonly(action, name, exc):
    """
    Edit file permissions and remove that file if it's read-only.
    """
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def create_template(
    name: typing.Optional[str] = "new_project",
    allow_only_empty: typing.Optional[bool] = True,
    url: typing.Optional[str] = GIT_TEMPLATE_URL,
):
    """
    Function to create project templates automatically. Second param kind of useless.
    -> create folders
    -> clone project template from github
    -> initialize git
    -> initialize poetry
    :param name: The name of new project.
    :param allow_only_empty: If True, will not create folders if directory is not empty.
    :param url: The url of the project template, default is set on codebase.
    """
    # read args when this file is invoked

    if not os.listdir():  # check if path is empty. NOTE: add "not"
        logger.info(f"creating project with name '{name}'")
        subprocess.run(f"mkdir {name}", shell=True, capture_output=True)
        subprocess.run(f"poetry init", shell=True, capture_output=True, cwd=name)
        # change working directory to the one created
        subprocess.run(
            r'"c:\Program Files\Git\bin\git.exe" init',  # run init with the path of git
            shell=True,
            capture_output=True,
        )
        logger.info("initialized git")
        subprocess.run(
            r'"c:\Program Files\Git\bin\git.exe" checkout -b main',
            shell=True,
            capture_output=True,
        )
        logger.info("switched branch to 'main'")
        subprocess.run(f"{GIT_PATH} clone {url}", shell=True, capture_output=True)
        logger.info("cloned project template files")
        files = os.listdir(f"./python-project-template")
        files.__delitem__(files.index(".git"))  # delete .git from the files to move
        for file in files:
            shutil.move(f"./python-project-template/{file}", f".")
        # Delete the folder "python-project-template"
        if os.path.exists("./python-project-template"):
            shutil.rmtree("./python-project-template", onerror=del_even_readonly)
        # shutil.rmtree("./python-project-template")
        logger.info("Successfully created project files github and moved them")
        logger.info("Running 'poetry install', this may take a while...")
        subprocess.run("poetry install", shell=True, capture_output=True, timeout=180.0)
        logger.info("installed poetry environment packages")
    else:
        logger.warning("Not an empty directory, aborting")


if __name__ == "__main__":
    # read args when this file is invoked
    args = read_user_args(sys.argv[1:])
    create_template(args.name, allow_only_empty=True, url=args.url)
