from contextlib import contextmanager
from pathlib import Path

from invoke import task

PYTHON_VERSION = "python3.10"


class Venv:
    """Misc. commands for handling virtual envs"""

    _cur_dir = Path(__file__).parent
    _venv_dir = _cur_dir / ".venv"
    _activate_path = _venv_dir / "bin" / "activate"
    _activate = ". {}".format(_activate_path)
    _build = f"{PYTHON_VERSION} -m venv {_venv_dir}"
    _requirements_sha = Path(_cur_dir) / "requirements_sha.txt"

    @classmethod
    @contextmanager
    def _virtualenv(cls, c):
        with c.cd(cls._cur_dir), c.prefix(cls._activate):
            yield

    @classmethod
    def _setup_venv(cls, c):
        if not cls._venv_dir.exists():
            c.run(cls._build)

        old_hash = ""
        new_hash = c.run("sha512sum requirements.txt").stdout.split(" ")[0]

        if cls._requirements_sha.exists():
            with cls._requirements_sha.open("r") as hash_fh:
                old_hash = hash_fh.readline()

        if old_hash != new_hash:
            print("New requriements, upgrading pip")
            with cls._virtualenv(c):
                c.run("pip install --upgrade pip")
                c.run("pip install -r requirements.txt", hide=False, echo=True)
            with cls._requirements_sha.open("w") as hash_fh:
                hash_fh.write(new_hash)

    @classmethod
    @contextmanager
    def virtualenv(cls, c):
        cls._setup_venv(c)
        with cls._virtualenv(c):
            yield


@task
def plot_map(c):
    with Venv.virtualenv(c):
        c.run(f"python plot_map.py")
