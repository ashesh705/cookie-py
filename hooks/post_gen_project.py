""" Post-project generation tasks"""

import os
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger


def trace(f: Callable) -> Callable:
    """Decorator to trace a function execution"""

    def _(*args: Any, **kwargs: Any) -> Any:
        start = datetime.now()

        ret = f(*args, **kwargs)
        end = datetime.now()

        time_elapsed = (end - start).total_seconds() * 1000  # in ms
        logger.info(f"Completed in {time_elapsed:.0f} ms")

        return ret

    return _


# ToDo - Name it better
class Failure(Exception):
    """Exception to raise if any step fails"""

    pass


def run(cmd: list, shell: bool = False) -> str:
    """Helper function to run system commands"""

    try:
        s = subprocess.run(cmd, shell=shell, check=True, capture_output=True)
    except subprocess.CalledProcessError as error:
        out = error.stderr or error.stdout
        raise Failure(out.decode().strip())

    return s.stdout.decode().strip()


class Git:
    command = "git"

    @classmethod
    def is_repository(cls, directory: Path) -> bool:
        """Check if the given directory is a valid git repository"""

        git_directory = directory / ".git"
        return git_directory in filter(Path.is_dir, directory.iterdir())

    @classmethod
    @trace
    def init(cls, directory: Path) -> bool:
        """Initialize a git repository in the given directory"""

        if directory.is_dir() is False:
            raise NotADirectoryError(f"{directory} is not a valid directory")

        if cls.is_repository(directory):
            logger.info(f"{directory} already has git initialized, skipping")
            return False

        logger.info(f"Initializing a git repository in {directory}")

        os.chdir(directory)
        run([cls.command, "init"])

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

        s = run([cls.command, "install", "-l"], shell=True)
        versions = s.split()

        # Restrict to python 3
        return [v for v in versions if v.startswith("3")]

    @classmethod
    def is_installed(cls, ver: str) -> bool:
        """Check if the given python version is installed"""

        return ver in cls.get_installed_versions()

    @classmethod
    @trace
    def install(cls, ver: str) -> bool:
        """Install the given python version"""

        if cls.is_installed(ver):
            logger.info(f"{ver} is already installed, skipping installation")
            return False

        logger.info(f"Installing python version {ver}")
        run([cls.command, "install", ver], shell=True)

        return True

    @classmethod
    @trace
    def uninstall(cls, ver: str) -> bool:
        """Uninstall the given python version"""

        if not cls.is_installed(ver):
            logger.info(f"{ver} is not installed, cannot uninstall")
            return False

        logger.info(f"Uninstalling python version {ver}")
        run([cls.command, "uninstall", ver], shell=True)

        return True

    @classmethod
    @trace
    def set_active(cls, ver: str, directory: Path) -> bool:
        """Set the given python version as active in the given directory"""

        if directory.is_dir() is False:
            raise NotADirectoryError(f"{directory} is not a valid directory")

        if not cls.is_installed(ver):
            logger.info(f"{ver} is not installed, cannot set as active")
            return False

        logger.info(f"Setting python version {ver} as active in {directory}")

        os.chdir(directory)
        run([cls.command, "local", ver], shell=True)

        return True

    @classmethod
    def get_path_for_active_python(cls, directory: Path) -> Path:
        """Get the path for active python in the given directory"""

        if directory.is_dir() is False:
            raise NotADirectoryError(f"{directory} is not a valid directory")

        os.chdir(directory)
        s = run([cls.command, "which", "python"], shell=True)

        path = Path(s)
        if not path.exists():
            raise EnvironmentError(
                f"No installed python version set in {directory}"
            )

        return path


class Poetry:  # pragma: no cover
    """Coverage disabled as these cannot be tested in CI environment"""

    command = "poetry"

    @classmethod
    @trace
    def configure(cls, directory: Path) -> None:
        """
        Configure poetry to use given python version in given directory.
        This will create a virtual environment if one does not already exist.
        """

        if directory.is_dir() is False:
            raise NotADirectoryError(f"{directory} is not a valid directory")

        path = PyEnv.get_path_for_active_python(directory)
        logger.info(f"Configuring poetry to use {path}")

        os.chdir(directory)
        out = run([cls.command, "env", "use", str(path)])

        for s in out.split():
            logger.info(s)


if __name__ == "__main__":
    try:
        # Initialize a git repo in the current directory
        current_dir = Path.cwd()
        Git.init(current_dir)

        # Install the required python version and mark it active
        py_ver = "{{ cookiecutter.python_version }}"
        PyEnv.install(py_ver)
        PyEnv.set_active(py_ver, current_dir)

        # Configure poetry to use the python version in current directory.
        # This will create a new virtual environment.
        # This step needs a pyproject.toml, which should be already generated
        Poetry.configure(current_dir)
    except Failure as e:
        logger.error(str(e))
        sys.exit(1)
