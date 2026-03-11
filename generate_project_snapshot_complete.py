import argparse
from pathlib import Path

DEFAULT_OUTPUT_FILE = "PROJECT_SNAPSHOT_COMPLETE.txt"

# משאירים רק cache/git בחוץ כדי לא להכניס זבל מוחלט
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
}

IGNORE_FILE_NAMES = {
    "Thumbs.db",
}

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
    ".env",
    ".env.example",
    ".gitignore",
    ".dockerignore",
    ".eslintrc.json",
    ".prettierrc",
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
    ".sh",
    ".cfg",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".css",
    ".html",
    ".svg",
    ".xml",
    ".bat",
    ".ps1",
    ".mako",
    ".request",
    ".yaml",
    ".env",
    ".example",
    ".lock",
    ".log",
    ".db",
}

# אם תרצה להכניס גם קבצים בינאריים "כמצביעים בלבד" בלי תוכן,
# נשאיר אותם בעץ אבל לא נדפיס את ה-bytes עצמם.
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".wav",
    ".mp3",
    ".mp4",
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".pdf",
}


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

    if file_path.suffix in INCLUDE_EXTENSIONS:
        return True

    # גם קבצים בלי סיומת או עם סיומת לא מוכרת – אם הם טקסט, נכניס
    if is_probably_text(file_path):
        return True

    # קבצים בינאריים נכניס רק כמטא־דאטה, לא כתוכן
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
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

        files.append(path)

    return files


def write_file_content(f, root: Path, file_path: Path):
    relative = file_path.relative_to(root)

    f.write("=" * 100 + "\n")
    f.write(f"FILE: {relative}\n")
    f.write("=" * 100 + "\n")

    try:
        suffix = file_path.suffix.lower()

        if suffix in BINARY_EXTENSIONS and not is_probably_text(file_path):
            try:
                size = file_path.stat().st_size
            except Exception:
                size = "unknown"

            f.write(f"[Binary file not printed as text | size={size} bytes]\n\n")
            return

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
            write_file_content(f, root, file_path)

    print("\nSnapshot created successfully!\n")
    print(f"Output file: {output_file}")
    print(f"Files included: {len(files)}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a near-complete project snapshot with almost all files."
    )

    parser.add_argument(
        "--root",
        default=".",
        help="Project root folder",
    )

    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT_FILE,
        help="Output file name",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_file = Path(args.out).resolve()

    write_snapshot(root, output_file)


if __name__ == "__main__":
    main()
