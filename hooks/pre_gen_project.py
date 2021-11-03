""" Validate input parameters for project generation"""

import sys

from loguru import logger


class Unsupported(Exception):
    """Exception thrown in case of unsupported parameters"""

    pass


class PyVersion:
    # ToDo - Find out min supported python version
    MIN_PYTHON_VERSION = "3.0.0"

    @classmethod
    def check(cls, ver: str) -> None:
        """Check if supplied python version is supported"""

        logger.info(f"Checking support for python version {ver}")
        if ver < cls.MIN_PYTHON_VERSION:
            raise Unsupported(
                f"Python version {ver} is not supported, "
                f"need at least {cls.MIN_PYTHON_VERSION}"
            )


if __name__ == "__main__":
    try:
        # Test if the required python version is supported
        py_ver = "{{ cookiecutter.python_version }}"
        PyVersion.check(py_ver)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
