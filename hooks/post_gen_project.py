""" Post-project generation tasks"""

import json
import logging
import os
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple, Optional

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)


def trace(func: Callable) -> Callable:
    """Decorator to trace a function execution"""

    def _(*args: Any, **kwargs: Any) -> Any:
        start = datetime.now()

        ret = func(*args, **kwargs)
        end = datetime.now()

        time_elapsed = (end - start).total_seconds() * 1000  # in ms
        logger.info(f"Completed in {time_elapsed:,.0f} ms")

        return ret

    return _


class Failure(Exception):
    """Exception to raise if any step fails"""

    pass


class _Task(NamedTuple):
    """Task to execute during cleanup stage"""

    func: Callable
    args: Optional[tuple] = None


def run(cmd: list) -> str:
    """Helper function to run system commands"""

    try:
        s = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as error:
        out = error.stderr or error.stdout
        raise Failure(out.decode().strip())

    return s.stdout.decode("iso-8859-1").strip()


class PyEnv:  # pragma: no cover
    """Coverage disabled as this cannot be tested in CI environment"""

    command = "pyenv"

    @staticmethod
    def _is_python_version(s: str) -> bool:
        """Check whether the given string represents a valid python version"""

        return s.startswith("2") or s.startswith("3")

    @classmethod
    def get_installed_versions(cls) -> list[str]:
        """Get a list of installed python versions"""

        pyenv_root = os.getenv("PYENV_ROOT")
        if pyenv_root is None:
            raise Failure("PYENV_ROOT is not configured")

        root_dir = Path(pyenv_root)
        version_dir = root_dir / "versions"

        return [i.name for i in version_dir.iterdir() if i.is_dir()]

    @classmethod
    def get_all_versions(cls) -> list[str]:
        """Get a list of all available python versions"""

        s = run([cls.command, "install", "-l"])
        versions = s.split()

        return list(filter(cls._is_python_version, versions))

    @classmethod
    def is_installed(cls, ver: str) -> bool:
        """Check if the given python version is installed"""

        return ver in cls.get_installed_versions()

    @classmethod
    def can_install(cls, ver: str) -> bool:
        """Check if the given python version can be installed"""

        return ver in cls.get_all_versions()

    @classmethod
    @trace
    def install(cls, ver: str) -> bool:
        """Install the given python version"""

        if cls.is_installed(ver):
            logger.info(f"{ver} is already installed, skipping installation")
            return False

        if not cls.can_install(ver):
            raise Failure(f"{ver} is not available for installation")

        logger.info(f"Installing python version {ver}")
        run([cls.command, "install", ver])

        return True

    @classmethod
    @trace
    def uninstall(cls, ver: str) -> bool:
        """Uninstall the given python version"""

        if not cls.is_installed(ver):
            logger.info(f"{ver} is not installed, cannot uninstall")
            return False

        logger.info(f"Uninstalling python version {ver}")
        run([cls.command, "uninstall", ver])

        return True

    @classmethod
    @trace
    def set_active(cls, directory: Path, ver: str) -> None:
        """Set the given python version as active in the given directory"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        if not cls.is_installed(ver):
            raise Failure(f"{ver} is not installed, cannot set as active")

        logger.info(f"Setting python version {ver} as active in {directory}")

        os.chdir(directory)
        run([cls.command, "local", ver])

    @classmethod
    def get_path(cls, directory: Path) -> Path:
        """Get the path for active python in the given directory"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        os.chdir(directory)
        s = run([cls.command, "which", "python"])

        path = Path(s)
        if not path.exists():
            raise Failure(f"No installed python version set in {directory}")

        return path


class Git:  # pragma: no cover
    """Coverage disabled as this cannot be tested in CI environment"""

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
            raise Failure(f"{directory} is not a valid directory")

        if cls.is_repository(directory):
            logger.info(f"{directory} already has git initialized, skipping")
            return False

        logger.info(f"Initializing a git repository in {directory}")

        os.chdir(directory)
        run([cls.command, "init"])

        return True


class VirtualEnv:  # pragma: no cover
    """Coverage disabled as this cannot be tested in CI environment"""

    command = "poetry"

    @classmethod
    @trace
    def init(cls, directory: Path) -> None:
        """Initialize a virtual environment for the given directory"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        path = PyEnv.get_path(directory)
        logger.info(f"Initializing virtual environment against {path}")

        os.chdir(directory)
        run([cls.command, "env", "use", str(path)])

    @classmethod
    @trace
    def remove(cls, directory: Path) -> None:
        """Remove the virtual environment for the given directory"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        path = PyEnv.get_path(directory)
        logger.info(f"Removing virtual environment against {path}")

        os.chdir(directory)
        run([cls.command, "env", "remove", str(path)])


class PackageManager:  # pragma: no cover
    """Coverage disabled as this cannot be tested in CI environment"""

    command = "poetry"

    @classmethod
    @trace
    def install(cls, directory: Path, packages: list[str]) -> None:
        """Install the given packages"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        logger.info(f"Installing dependencies - {', '.join(packages)}")

        os.chdir(directory)
        run([cls.command, "add"] + packages)

    @classmethod
    @trace
    def install_dev(cls, directory: Path, packages: list[str]) -> None:
        """Install the given packages as dev dependencies"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        logger.info(f"Installing dev dependencies - {', '.join(packages)}")

        os.chdir(directory)
        run([cls.command, "add", "-D"] + packages)


class PreCommit:  # pragma: no cover
    """Coverage disabled as this cannot be tested in CI environment"""

    command = "pre-commit"

    @classmethod
    @trace
    def install(cls, directory: Path) -> None:
        """Install the pre-commit hooks"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        logger.info("Installing pre-commit hooks")

        os.chdir(directory)
        run([cls.command, "install"])

    @classmethod
    @trace
    def run(cls, directory: Path) -> None:
        """Install the pre-commit hooks"""

        if directory.is_dir() is False:
            raise Failure(f"{directory} is not a valid directory")

        logger.info("Running pre-commit hooks on all current files")

        os.chdir(directory)
        run([cls.command, "run", "--all-files"])


if __name__ == "__main__":
    cleanup_stack: list[_Task] = []

    try:
        # Install the required python version
        py_ver = "{{ cookiecutter.python_version }}"
        installed = PyEnv.install(py_ver)

        if installed:
            cleanup_stack.insert(0, _Task(func=PyEnv.uninstall, args=(py_ver,)))

        # Get the project root
        project_root = Path.cwd()

        # Initialize a git repo in the project root
        Git.init(project_root)

        # Mark the active python version in the project directory
        PyEnv.set_active(project_root, py_ver)

        # Initialize a virtual environment in the project directory
        VirtualEnv.init(project_root)
        cleanup_stack.insert(
            0, _Task(func=VirtualEnv.remove, args=(project_root,))
        )

        # Install required dependencies
        file = project_root / "package-list.json"
        with file.open() as f:
            package_list = json.load(f)

        file.unlink()

        dependencies, dev_dependencies = (
            package_list["required"],
            package_list["dev"],
        )

        PackageManager.install(project_root, dependencies)
        PackageManager.install_dev(project_root, dev_dependencies)

        # Configure git hooks, install and run once
        PreCommit.install(project_root)
        PreCommit.run(project_root)
    except Exception as e:
        logger.error(str(e))

        # Cleanup
        for task in cleanup_stack:
            if task.args is None:
                task.func()
            else:
                task.func(*task.args)

        sys.exit(1)
