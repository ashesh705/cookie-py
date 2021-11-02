""" Fixtures for testing the project"""

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from random import choices
from string import ascii_letters

import pytest
from loguru import logger


def _get_random_string(length: int) -> str:
    """Return a random string of specified length"""

    return "".join(choices(ascii_letters, k=length))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Returns path to a temporary directory"""

    current_dir = Path.cwd()

    location = Path(tempfile.gettempdir())
    d = location / _get_random_string(10)

    yield d

    if Path.cwd() != current_dir:
        os.chdir(current_dir)

    if d.exists():
        logger.debug(f"Deleting {d}")
        shutil.rmtree(d)
