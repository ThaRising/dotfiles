from pathlib import Path
import shutil

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
        ".gitignore", ".idea", ".git", "README.md", "install.py"
    )
    items_to_copy = [
        item for item in CURRENT_DIR.iterdir()
        if item.name not in items_to_ignore
    ]

    for item in items_to_copy:
        recursive_copymerge(item)
