""" Test cases for check functions"""

import pytest

from hooks.pre_gen_project import PyVersion, Unsupported


class TestPyVersion:
    correct = "3.9.0"
    incorrect = "2.9.0"

    def test_correct(self) -> None:
        PyVersion.check(self.correct)

    def test_incorrect(self) -> None:
        with pytest.raises(Unsupported):
            PyVersion.check(self.incorrect)
