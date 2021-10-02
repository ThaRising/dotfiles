#!/usr/bin/python3
import shutil
import subprocess
from pathlib import Path

# TEST_OVERRIDE_DEST = "/tmp/kochbehome"
TEST_OVERRIDE_DEST = ""


def recursive_copymerge(file_or_dir: Path, force: bool = True):
    src_path = file_or_dir
    dest_path = USER_HOME_DIR / file_or_dir.relative_to(CURRENT_DIR)
    if file_or_dir.is_file():
        if not dest_path.exists() or force:
            shutil.copy(src_path, dest_path)
        return
    elif file_or_dir.is_dir():
        if not dest_path.exists():
            dest_path.mkdir()
        for i in file_or_dir.iterdir():
            recursive_copymerge(i)


if __name__ == '__main__':
    USER_HOME_DIR = TEST_OVERRIDE_DEST or Path.home()
    CURRENT_DIR = Path(__file__).parent

    items_to_ignore = (
        ".gitignore", ".idea", ".git", "README.md", "install.py", "dconf"
    )
    items_to_copy = [
        item for item in CURRENT_DIR.iterdir()
        if item.name not in items_to_ignore
    ]

    for item in items_to_copy:
        recursive_copymerge(item)

    print("Copying of Configuration-Files done.")
    print()
    print("Importing dconf Shortcuts...")

    dconf_dir_content = (CURRENT_DIR / "dconf").iterdir()
    for config in dconf_dir_content:
        dconf_path = "/" + config.name.replace(".", "/") + "/"
        result = subprocess.run(
            f"dconf load {dconf_path} < {config.absolute()!s}",
            capture_output=False,
            shell=True
        )

    print("Completed dconf Imports.")
    print("Symlinking custom Scripts...")

    scripts_dir_content = (CURRENT_DIR / ".scripts").iterdir()
    for script in scripts_dir_content:
        if script.name.endswith(".global"):
            scripts_path = USER_HOME_DIR / '.scripts'
            # Symlink from myscript.global to myscript in the same dir
            subprocess.run(
                f"ln -s {(scripts_path / script.name)!s} "
                f"{(scripts_path / script.name.replace('.global', ''))!s}",
                shell=True
            )
            # Symlink all myscript.global scripts to PATH
            subprocess.run(
                f"sudo ln -s {(USER_HOME_DIR / '.scripts' / script.name)!s} "
                f"/usr/bin/{script.name.replace('.global', '')}",
                shell=True
            )
