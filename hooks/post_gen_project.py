""" Post-project generation tasks"""

import os
import subprocess
import sys
from pathlib import Path

from loguru import logger


def initialize_git_repo(directory: Path) -> None:
    """Initialize a git repository in the given directory"""

    if directory.is_dir() is False:
        raise NotADirectoryError(f"{directory} is not a valid directory")

    os.chdir(directory)
    subprocess.run(["git", "init"])


if __name__ == "__main__":
    try:
        initialize_git_repo(Path.cwd())
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
