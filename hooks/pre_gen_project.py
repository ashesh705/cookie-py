""" Validate input parameters for project generation"""

import sys

from loguru import logger


class Unsupported(Exception):
    """Exception thrown in case of unsupported parameters"""

    pass


# ToDo - Find out min python version
_MIN_PYTHON_VERSION = "3.0.0"


def check_py_version(ver: str) -> None:
    if ver < _MIN_PYTHON_VERSION:
        raise Unsupported(
            f"Python version {ver} is not supported, "
            f"need at least {_MIN_PYTHON_VERSION}"
        )


if __name__ == "__main__":
    try:
        py_ver = "{{ cookiecutter.python_version }}"
        check_py_version(py_ver)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
