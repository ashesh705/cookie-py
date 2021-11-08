""" Validate input parameters for project generation"""

import logging
import sys
from collections.abc import Callable
from datetime import datetime
from typing import Any

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)


def trace(f: Callable) -> Callable:
    """Decorator to trace a function execution"""

    def _(*args: Any, **kwargs: Any) -> Any:
        start = datetime.now()

        ret = f(*args, **kwargs)
        end = datetime.now()

        time_elapsed = (end - start).total_seconds() * 1000  # in ms
        logger.info(f"Completed in {time_elapsed:,.0f} ms")

        return ret

    return _


class Unsupported(Exception):
    """Exception thrown in case of unsupported parameters"""

    pass


class PyVersion:
    # ToDo - Find out min supported python version
    MIN_PYTHON_VERSION = "3.0.0"

    @classmethod
    @trace
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
