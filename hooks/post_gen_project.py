""" Post-project generation tasks"""

import os
import subprocess
import sys
from pathlib import Path

from loguru import logger


class Git:
    command = "git"

    @classmethod
    def is_repository(cls, directory: Path) -> bool:
        """Check if the given directory is a valid git repository"""

        git_directory = directory / ".git"
        return git_directory in filter(Path.is_dir, directory.iterdir())

    @classmethod
    def init(cls, directory: Path) -> bool:
        """Initialize a git repository in the given directory"""

        if directory.is_dir() is False:
            raise NotADirectoryError(f"{directory} is not a valid directory")

        if cls.is_repository(directory):
            logger.info(f"{directory} already has git initialized, skipping")
            return False

        logger.info(f"Initializing a git repository in {directory}")

        os.chdir(directory)
        subprocess.run([cls.command, "init"])

        return True


class PyEnv:  # pragma: no cover
    """Coverage disabled as these cannot be tested in CI environment"""

    command = "pyenv"

    @classmethod
    def get_installed_versions(cls) -> list[str]:
        """Get a list of installed python versions"""

        pyenv_root = os.getenv("PYENV_ROOT")
        if pyenv_root is None:
            raise EnvironmentError("PYENV_ROOT is not configured")

        root_dir = Path(pyenv_root)
        version_dir = root_dir / "versions"

        return [f.name for f in version_dir.iterdir() if f.is_dir()]

    @classmethod
    def get_all_versions(cls) -> list[str]:
        """Get a list of all available python versions"""

        s = subprocess.run(
            [cls.command, "install", "-l"], shell=True, capture_output=True
        )
        versions = s.stdout.decode().strip().split()

        # Restrict to python 3
        return [v for v in versions if v.startswith("3")]

    @classmethod
    def is_installed(cls, ver: str) -> bool:
        """Check if the given python version is installed"""

        return ver in cls.get_installed_versions()

    @classmethod
    def install(cls, ver: str) -> bool:
        """Install the given python version"""

        if cls.is_installed(ver):
            logger.info(f"{ver} is already installed, skipping installation")
            return False

        logger.info(f"Installing python version {ver}")
        subprocess.run([cls.command, "install", ver], shell=True)

        return True

    @classmethod
    def uninstall(cls, ver: str) -> bool:
        """Uninstall the given python version"""

        if not cls.is_installed(ver):
            logger.info(f"{ver} is not installed, cannot uninstall")
            return False

        logger.info(f"Uninstalling python version {ver}")
        subprocess.run([cls.command, "uninstall", ver], shell=True)

        return True

    @classmethod
    def set_active(cls, ver: str, directory: Path) -> bool:
        """Set the given python version as active in the given directory"""

        if directory.is_dir() is False:
            raise NotADirectoryError(f"{directory} is not a valid directory")

        if not cls.is_installed(ver):
            logger.info(f"{ver} is not installed, cannot set as active")
            return False

        logger.info(f"Setting python version {ver} as active in {directory}")

        os.chdir(directory)
        subprocess.run([cls.command, "local", ver], shell=True)

        return True


if __name__ == "__main__":
    try:
        # Initialize a git repo in the current directory
        current_dir = Path.cwd()
        Git.init(current_dir)

        # Install the required python version and mark it active
        py_ver = "{{ cookiecutter.python_version }}"
        PyEnv.install(py_ver)
        PyEnv.set_active(py_ver, current_dir)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
