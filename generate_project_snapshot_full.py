import argparse
from pathlib import Path

DEFAULT_OUTPUT_FILE = "PROJECT_SNAPSHOT_FULL.txt"

# תיקיות שלא נרצה להכניס
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".next",
    ".cache",
    ".mypy_cache",
    ".ruff_cache",
    "uploads",
    "tests_tmp_uploads",
}

# קבצים שלא נרצה
IGNORE_FILE_NAMES = {
    ".env",
    "test.db",
    "Thumbs.db",
}

# קבצים מיוחדים שצריך תמיד לקחת
SPECIAL_FILES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "alembic.ini",
    "entrypoint.sh",
    "pytest.ini",
    "README.md",
    "LICENSE",
    ".gitignore",
    ".dockerignore",
    ".env.example",
}

# סיומות שאנחנו כן רוצים
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
    ".sh",
    ".cfg",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".css",
    ".html",
    ".xml",
    ".mako",
}

# קבצים בינאריים/מדיה שלא נדפיס כתוכן
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".wav",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".pdf",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".db",
}

# קבצים גדולים מאוד יגרמו לפיצוץ מיותר
MAX_FILE_SIZE_BYTES = 2_000_000  # 2MB


def should_ignore(path: Path) -> bool:
    parts = set(path.parts)

    if parts & IGNORE_DIRS:
        return True

    if path.name in IGNORE_FILE_NAMES:
        return True

    return False


def is_probably_text(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(4096)

        if b"\x00" in chunk:
            return False

        chunk.decode("utf-8")
        return True

    except Exception:
        return False


def should_include(file_path: Path) -> bool:
    if file_path.name in SPECIAL_FILES:
        return True

    if file_path.suffix.lower() in INCLUDE_EXTENSIONS:
        return True

    # גם אם אין סיומת מוכרת, אבל זה טקסט, אפשר להכניס
    if is_probably_text(file_path):
        return True

    return False


def build_tree(root: Path) -> str:
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


def collect_files(root: Path):
    files = []

    for path in sorted(root.rglob("*")):
        if should_ignore(path):
            continue

        if not path.is_file():
            continue

        if not should_include(path):
            continue

        try:
            size = path.stat().st_size
        except OSError:
            continue

        if size > MAX_FILE_SIZE_BYTES:
            continue

        # בינארי לא נכניס כתוכן
        if path.suffix.lower() in BINARY_EXTENSIONS and not is_probably_text(path):
            continue

        files.append(path)

    return files


def write_snapshot(root: Path, output_file: Path):
    tree = build_tree(root)
    files = collect_files(root)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("PROJECT STRUCTURE\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"ROOT: {root.resolve()}\n\n")
        f.write(tree)
        f.write("\n\n\n")

        for file_path in files:
            relative = file_path.relative_to(root)

            f.write("=" * 100 + "\n")
            f.write(f"FILE: {relative}\n")
            f.write("=" * 100 + "\n")

            try:
                with open(file_path, "r", encoding="utf-8") as code:
                    f.write(code.read())
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="latin-1") as code:
                        f.write(code.read())
                except Exception as exc:
                    f.write(f"[Could not read file as text: {exc}]\n")
            except Exception as exc:
                f.write(f"[Could not read file: {exc}]\n")

            f.write("\n\n")

    print("\nSnapshot created successfully!\n")
    print(f"Output file: {output_file}")
    print(f"Files included: {len(files)}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a balanced project snapshot with all important code/config files."
    )

    parser.add_argument("--root", default=".", help="Project root folder")

    parser.add_argument("--out", default=DEFAULT_OUTPUT_FILE, help="Output file name")

    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_file = Path(args.out).resolve()

    write_snapshot(root, output_file)


if __name__ == "__main__":
    main()
