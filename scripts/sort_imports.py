"""Sort maintained Python imports with the pinned isort release."""

import subprocess
from pathlib import Path


def main() -> None:
    subprocess.run(
        [
            "uv",
            "tool",
            "run",
            "--from",
            "isort==9.0.2",
            "isort",
            "--profile",
            "black",
            "propstore",
            "tests",
            "scripts",
        ],
        cwd=Path(__file__).resolve().parent.parent,
        check=True,
    )


if __name__ == "__main__":
    main()
