#!/usr/bin/python3
import argparse
import os
import pwd
import shutil
import subprocess
from pathlib import Path
from typing import Tuple

CURRENT_DIR = Path(__file__).parent

ITEMS_TO_IGNORE = (
    ".gitignore", ".idea", ".git", "README.md", "install.py", "dconf"
)


def get_user_info(username: str) -> Tuple[str, int, int]:
    pw_record = pwd.getpwnam(username)
    user_home = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid
    return user_home, user_gid, user_uid


def demote(uid: int, gid: int):
    os.setgid(gid)
    os.setuid(uid)


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


def import_dconf_config() -> None:
    dconf_dir_content = (CURRENT_DIR / "dconf").iterdir()
    for config in dconf_dir_content:
        dconf_path = "/" + config.name.replace(".", "/") + "/"
        subprocess.Popen(
            f"dconf load {dconf_path} < {config.absolute()!s}",
            shell=True, preexec_fn=demote(*userinfo)
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--user', dest='user',
        help='User to install dotfiles for.'
    )
    args = parser.parse_args()

    # Uncomment this for Testing:
    # TEST_OVERRIDE_DEST = "/tmp/kochbehome"
    TEST_OVERRIDE_DEST = ""
    USER_HOME_DIR = TEST_OVERRIDE_DEST or get_user_info(args.user)[0]

    print("Copying configuration files...")

    items_to_copy = [
        item for item in CURRENT_DIR.iterdir()
        if item.name not in ITEMS_TO_IGNORE
    ]
    for item in items_to_copy:
        recursive_copymerge(item)

    print("Copying of Configuration-Files done.")

    *_, userinfo = get_user_info(args.user)

    print("Symlinking custom Scripts...")

    scripts_dir_content = (CURRENT_DIR / ".scripts").iterdir()
    SCRIPTS_PATH = USER_HOME_DIR / '.scripts'
    for script in scripts_dir_content:
        # Make all scripts executable
        subprocess.run(f"chmod +x {(SCRIPTS_PATH / script.name)!s}", shell=True)

        if script.name.endswith(".global"):
            # Symlink from myscript.global to myscript in the same dir
            subprocess.Popen(
                f"ln -s {(SCRIPTS_PATH / script.name)!s} "
                f"{(SCRIPTS_PATH / script.name.replace('.global', ''))!s}",
                shell=True, preexec_fn=demote(*userinfo)
            )
            # Symlink all myscript.global scripts to PATH
            subprocess.run(
                f"ln -s {(SCRIPTS_PATH / script.name)!s} "
                f"/usr/bin/{script.name.replace('.global', '')}",
                shell=True
            )

    print("Symlinking finished.")
    print()
    print("Importing dconf Shortcuts...")

    import_dconf_config()

    print("Completed dconf Imports.")
