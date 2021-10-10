#!/usr/bin/python3
import argparse
import os
import pwd
import shutil
import subprocess
from pathlib import Path
from typing import Union, Optional


CURRENT_DIR = Path(__file__).parent
ITEMS_TO_IGNORE = (
    ".gitignore", ".idea", ".git", "README.md", "install.py", "dconf"
)


class User:
    def __init__(self, name: str = "root") -> None:
        pw_record = pwd.getpwnam(name)
        self.name = name
        self.home = pw_record.pw_dir
        self.uid = pw_record.pw_uid
        self.gid = pw_record.pw_gid

    def _demote(self) -> None:
        os.setgid(self.uid)
        os.setuid(self.gid)

    def import_dconf_config(self) -> None:
        dconf_dir_content = (CURRENT_DIR / "dconf").iterdir()
        for config in dconf_dir_content:
            dconf_path = "/" + config.name.replace(".", "/") + "/"
            subprocess.Popen(
                f"sudo -u {self.name} dconf load {dconf_path} < {config.absolute()!s}",
                shell=True, preexec_fn=self._demote()
            )

    def recursive_merge_files(self, file_or_dir: Path, force: bool = True):
        src_path = file_or_dir
        dest_path = USER_HOME_DIR / file_or_dir.relative_to(CURRENT_DIR)
        if file_or_dir.is_file():
            if not dest_path.exists() or force:
                shutil.copy(src_path, dest_path)
                os.chown(dest_path, uid=self.uid, gid=self.gid)
            return
        elif file_or_dir.is_dir():
            if not dest_path.exists():
                dest_path.mkdir()
            for i in file_or_dir.iterdir():
                self.recursive_merge_files(i)

    def run_command_as(
            self, cmd: Union[str, list], **kwargs
    ) -> Optional[subprocess.Popen[str]]:
        return subprocess.Popen(f"sudo -u {self.name} {cmd}", shell=True, **kwargs)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument(
    '--user', dest='user',
    help='User as which to run all operations, '
         'that do not require elevated privileges'
)
args = parser.parse_args()


if __name__ == '__main__':
    privileged_user = User("root")
    standard_user = User(args.user)

    # Uncomment this for Testing:
    # TEST_OVERRIDE_DEST = "/tmp/kochbehome"
    TEST_OVERRIDE_DEST = ""
    USER_HOME_DIR = Path(TEST_OVERRIDE_DEST or standard_user.home)

    print("Copying configuration files...")
    items_to_copy = [
        item for item in CURRENT_DIR.iterdir()
        if item.name not in ITEMS_TO_IGNORE
    ]
    for item in items_to_copy:
        standard_user.recursive_merge_files(item)
    print("Copying of Configuration-Files completed.")

    print("Symlinking custom Scripts...")
    scripts_dir_content = (CURRENT_DIR / ".scripts").iterdir()
    SCRIPTS_PATH = USER_HOME_DIR / '.scripts'
    os.chown(SCRIPTS_PATH, uid=standard_user.uid, gid=standard_user.gid)
    for script in scripts_dir_content:
        # Make all scripts executable
        subprocess.run(f"chmod +x {(SCRIPTS_PATH / script.name)!s}", shell=True)

        if script.name.endswith(".global"):
            # Symlink from myscript.global to myscript in the same dir
            standard_user.run_command_as(
                f"ln -s {(SCRIPTS_PATH / script.name)!s} "
                f"{(SCRIPTS_PATH / script.name.replace('.global', ''))!s}"
            )
            # Symlink all myscript.global scripts to PATH
            privileged_user.run_command_as(
                f"ln -s {(SCRIPTS_PATH / script.name)!s} "
                f"/usr/bin/{script.name.replace('.global', '')}"
            )
    print("Symlinking finished.")

    print("Importing dconf Shortcuts...")
    standard_user.import_dconf_config()
    print("Completed dconf Imports.")
