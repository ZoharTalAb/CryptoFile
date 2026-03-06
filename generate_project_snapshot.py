import os
from pathlib import Path

OUTPUT_FILE = "PROJECT_SNAPSHOT_BACKEND.txt"

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

INCLUDE_EXTENSIONS = {
    ".py",
    ".sql",
    ".txt",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".json",
}

SPECIAL_FILES = {"Dockerfile", "docker-compose.yml", "requirements.txt"}


def should_ignore(path):
    parts = set(path.parts)
    return bool(parts & IGNORE_DIRS)


def should_include(file_path):
    if file_path.name in SPECIAL_FILES:
        return True
    return file_path.suffix in INCLUDE_EXTENSIONS


def build_tree(root):
    lines = []

    for path in sorted(root.rglob("*")):
        if should_ignore(path):
            continue

        relative = path.relative_to(root)
        indent = "│   " * (len(relative.parts) - 1)

        if path.is_dir():
            lines.append(f"{indent}📁 {path.name}/")
        else:
            lines.append(f"{indent}📄 {path.name}")

    return "\n".join(lines)


def collect_files(root):
    files = []

    for path in sorted(root.rglob("*")):
        if should_ignore(path):
            continue

        if path.is_file() and should_include(path):
            files.append(path)

    return files


def write_snapshot():
    root = Path(".")

    tree = build_tree(root)
    files = collect_files(root)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("PROJECT STRUCTURE\n")
        f.write("=" * 60 + "\n\n")
        f.write(tree)
        f.write("\n\n\n")

        for file_path in files:
            relative = file_path.relative_to(root)

            f.write("=" * 60 + "\n")
            f.write(f"FILE: {relative}\n")
            f.write("=" * 60 + "\n")

            try:
                with open(file_path, "r", encoding="utf-8") as code:
                    f.write(code.read())
            except:
                f.write("[Could not read file]\n")

            f.write("\n\n")


if __name__ == "__main__":
    write_snapshot()
    print(f"\nSnapshot created: {OUTPUT_FILE}\n")
