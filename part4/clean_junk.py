import os
import shutil

# Patterns of useless files to remove
USELESS_PATTERNS = [
    ".pyc",
    ".pyo",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "Zone.Identifier",
    "__pycache__",
]

def is_useless(filename):
    for pattern in USELESS_PATTERNS:
        if filename.endswith(pattern) or filename == pattern:
            return True
    return False

def clean_useless_files(root_dir="."):
    removed_files = []
    removed_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):  # topdown=False ensures we check subdirectories last
        # Remove files
        for filename in filenames:
            if is_useless(filename):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                except Exception as e:
                    print(f"Could not remove file {file_path}: {e}")

        # Remove __pycache__ and similar dirs
        for dirname in dirnames:
            if dirname == "__pycache__":
                dir_path = os.path.join(dirpath, dirname)
                try:
                    # Remove the __pycache__ directory
                    shutil.rmtree(dir_path)
                    removed_dirs.append(dir_path)
                except Exception as e:
                    print(f"Could not remove dir {dir_path}: {e}")

    print(f"Removed files: {len(removed_files)}")
    print(f"Removed dirs: {len(removed_dirs)}")
    if removed_files:
        print("Files removed:")
        for f in removed_files:
            print("  ", f)
    if removed_dirs:
        print("Dirs removed:")
        for d in removed_dirs:
            print("  ", d)

if __name__ == "__main__":
    clean_useless_files(".")
