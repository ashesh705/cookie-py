""" Test cases for python environment setup"""

from pathlib import Path
from random import choice

import pytest
from loguru import logger

from hooks.post_gen_project import PyEnv


@pytest.mark.no_ci
class TestPyEnv:
    """This test suite is not supposed to run in CI environment"""

    @staticmethod
    def get_random_uninstalled_version() -> str:
        """
        Get a python version, currently uninstalled.

        This will be used to carry out tests in this suite,
        avoiding any corruption of installed python versions.
        """

        all_versions = PyEnv.get_all_versions()
        installed = PyEnv.get_installed_versions()
        uninstalled = set(all_versions) - set(installed)

        return choice(list(uninstalled))

    def test_get_installed_versions(self, current_python_version: str) -> None:
        versions = PyEnv.get_installed_versions()
        logger.debug(versions)

        assert current_python_version in versions

    def test_get_all_versions(self, current_python_version: str) -> None:
        versions = PyEnv.get_all_versions()
        logger.debug(versions)

        assert current_python_version in versions

    def test_install_non_existing(self) -> None:
        ver = self.get_random_uninstalled_version()

        assert PyEnv.install(ver) is True
        assert ver in PyEnv.get_installed_versions()

        PyEnv.uninstall(ver)

    def test_install_existing(self, current_python_version: str) -> None:
        assert PyEnv.install(current_python_version) is False

    def test_uninstall_existing(self) -> None:
        ver = self.get_random_uninstalled_version()
        PyEnv.install(ver)

        assert PyEnv.uninstall(ver) is True
        assert ver not in PyEnv.get_installed_versions()

    def test_uninstall_non_existing(self) -> None:
        ver = self.get_random_uninstalled_version()
        assert PyEnv.uninstall(ver) is False

    def test_set_active_existing(
        self, temp_dir: Path, current_python_version: str
    ) -> None:
        logger.debug(f"Creating directory {temp_dir}")
        temp_dir.mkdir()

        assert PyEnv.set_active(current_python_version, temp_dir) is True

        file = temp_dir / ".python-version"
        with file.open() as f:
            contents = f.read()

        assert current_python_version in contents

    def test_set_active_non_existing(self, temp_dir: Path) -> None:
        logger.debug(f"Creating directory {temp_dir}")
        temp_dir.mkdir()

        ver = self.get_random_uninstalled_version()
        assert PyEnv.set_active(ver, temp_dir) is False
