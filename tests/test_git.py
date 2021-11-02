""" Test cases for git related tasks"""

from pathlib import Path

import pytest
from loguru import logger

from hooks.post_gen_project import initialize_git_repo


def test_git_repo_valid(temp_dir: Path) -> None:
    logger.debug(f"Creating directory {temp_dir}")
    temp_dir.mkdir()

    initialize_git_repo(temp_dir)

    assert ".git" in map(lambda p: p.name, temp_dir.glob("*"))


def test_git_repo_invalid(temp_dir: Path) -> None:
    with pytest.raises(NotADirectoryError):
        initialize_git_repo(temp_dir)
