""" Test cases for git related tasks"""

from pathlib import Path

import pytest
from loguru import logger

from hooks.post_gen_project import Git


class TestGit:
    def test_empty_dir(self, temp_dir: Path) -> None:
        logger.debug(f"Creating directory {temp_dir}")
        temp_dir.mkdir()

        assert Git.init(temp_dir) is True
        assert Git.is_repository(temp_dir) is True

    def test_pre_existing_repo(self, temp_dir: Path) -> None:
        logger.debug(f"Creating directory {temp_dir}")
        temp_dir.mkdir()
        Git.init(temp_dir)

        assert Git.init(temp_dir) is False
        assert Git.is_repository(temp_dir) is True

    def test_invalid_dir(self, temp_dir: Path) -> None:
        with pytest.raises(NotADirectoryError):
            Git.init(temp_dir)
