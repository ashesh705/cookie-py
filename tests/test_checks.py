""" Test cases for check functions"""

import pytest

from hooks.pre_gen_project import Unsupported, check_py_version


def test_check_correct_py_version() -> None:
    v = "3.9.0"
    check_py_version(v)


def test_check_incorrect_py_version() -> None:
    v = "2.9.0"
    with pytest.raises(Unsupported):
        check_py_version(v)
