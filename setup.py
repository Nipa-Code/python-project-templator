import argparse
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import typing

from loguru import logger

aliases = {
    "gs": "git status",
    "gl": "git log --oneline",
}  # These don't have any actual useful use

GIT_TEMPLATE_URL = "https://github.com/Nipa-Code/python-project-template.git"

"""
NOTE: Missing to Configure pre-commit.
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


def add_alias(name: str = "setup-project", command: str = None):
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
    :param name: The name of the file to be removed.
    """
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def create_template(
    name: typing.Optional[str] = "new_project",
    allow_only_empty: typing.Optional[bool] = True,
    url: typing.Optional[str] = GIT_TEMPLATE_URL,
):
    """
    Function to create project templates automatically. Second param is kind of useless for now.
    -> create folders
    -> clone project template from Github
    -> initialize git
    -> initialize poetry
    :param name: The name of new project.
    :param allow_only_empty: If True, will not create folders if directory is not empty.
    :param url: The url of the project template, default is set on codebase.
    """
    if not os.listdir():  # check if path is empty. NOTE: add "not" if it is not there
        logger.info(
            f"Creating template for project: '{name}', from: '{url}', Directory is empty"
        )
        subprocess.run(f"mkdir {name}", shell=True, capture_output=True)
        logger.debug("Created project folder")

        subprocess.run(
            "git init",  # run init with the path of git
            shell=True,
            capture_output=True,
        )
        logger.info("Initialized git")

        subprocess.run(
            "git -b main",
            shell=True,
            capture_output=True,
        )
        logger.info("Switched branch to 'main'")

        subprocess.run(f"git clone {url}", shell=True, capture_output=True)
        logger.info("Cloned project template files")

        files = os.listdir("./python-project-template")
        files.__delitem__(files.index(".git"))  # delete .git from the files to move
        for file in files:
            shutil.move(f"./python-project-template/{file}", ".")

        # Delete the folder "python-project-template"
        if os.path.exists("./python-project-template"):
            shutil.rmtree("./python-project-template", onerror=del_even_readonly)

        logger.debug("Successfully pulled project files from Github and moved them.")

        logger.debug("Running 'poetry install', this may take a while...")
        subprocess.run("poetry install", shell=True, capture_output=True, timeout=180.0)
        logger.info("Installed poetry environment packages")

        subprocess.run(
            "git add .",
            shell=True,
            capture_output=True,
        )
        logger.debug("Added all files to git")

        subprocess.run(
            "git commit -m 'initial commit'",
            shell=True,
            capture_output=True,
        )
        logger.debug("Succesfully ran git commit, files are now saved to git")
        logger.info("Finished setup, ready to go!")
    else:
        logger.warning("Not an empty directory, aborting!")


if __name__ == "__main__":
    # read args when this file is invoked
    args = read_user_args(sys.argv[1:])
    create_template(args.name, allow_only_empty=True, url=args.url)
