"""Verify local and cross-repository links in the public entrypoint documents."""

import argparse
import posixpath
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


REPOSITORIES = ("NaturalDAO", "NaturalDAO-2nd")
ENTRYPOINTS = ("README.md", "CONTRIBUTING.md", "SECURITY.md")
SURVEY = "PoL-Governance/research/PoL2-Jev-Typed-Literature-Survey"
ADDITIONAL_ENTRYPOINTS = {
    "media/README.md",
    f"{SURVEY}/README.md",
    f"{SURVEY}/CITATION.cff",
    f"{SURVEY}/paper/README.md",
    f"{SURVEY}/paper/arxiv_metadata.txt",
    f"{SURVEY}/paper/make_metadata.py",
}
MARKDOWN_LINK = re.compile(r"\]\(\s*(<[^>\n]+>|[^\s)]+)")
TEXT_REPOSITORY_LINK = re.compile(r'https://github\.com/naturaldao/[^)\s"<>}\\]+')
REPOSITORY_LINK = re.compile(
    r"/naturaldao/(NaturalDAO(?:-2nd)?)/(blob|tree)/main/(.+)"
)


def repository_paths(root):
    tree = subprocess.check_output(
        ["git", "-C", str(root), "ls-tree", "-r", "-z", "--name-only", "HEAD"],
        encoding="utf-8",
    )
    files = set(tree.rstrip("\0").split("\0"))
    directories = {
        str(parent) for file in files for parent in PurePosixPath(file).parents
    }
    return files, directories


def additional_entrypoints(files):
    for file in sorted(files):
        parts = PurePosixPath(file).parts
        if parts[0] == "Research" and file.endswith(".md") and "99-归档" not in parts:
            yield file
        elif file in ADDITIONAL_ENTRYPOINTS or (
            file.startswith(f"{SURVEY}/paper/") and file.endswith(".tex")
            and "review" not in parts
        ):
            yield file


def document_links(document, line):
    if document.endswith(".md"):
        return MARKDOWN_LINK.findall(line)
    return [link.rstrip(".") for link in TEXT_REPOSITORY_LINK.findall(line)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", choices=REPOSITORIES)
    parser.add_argument("companion", type=Path)
    args = parser.parse_args()

    companion = next(name for name in REPOSITORIES if name != args.repository)
    paths = {
        args.repository: repository_paths(Path.cwd()),
        companion: repository_paths(args.companion),
    }

    own_files, own_directories = paths[args.repository]
    local_candidates = own_files | own_directories

    failures = []
    checked = 0
    for entrypoint in (*ENTRYPOINTS, *additional_entrypoints(own_files)):
        for line_number, line in enumerate(
            Path(entrypoint).read_text(encoding="utf-8").splitlines(), start=1
        ):
            for link in document_links(entrypoint, line):
                target = urlsplit(link.strip("<>"))
                if not target.path:
                    continue
                path = unquote(target.path)
                if target.scheme or target.netloc:
                    match = REPOSITORY_LINK.fullmatch(path) if target.netloc == "github.com" else None
                    if not match:
                        continue
                    repository, kind, path = match.groups()
                    files, directories = paths[repository]
                    candidates = files if kind == "blob" else directories
                else:
                    path = (
                        path.lstrip("/") if path.startswith("/")
                        else posixpath.join(posixpath.dirname(entrypoint), path)
                    )
                    candidates = local_candidates
                checked += 1
                if posixpath.normpath(path) not in candidates:
                    failures.append(f"{entrypoint}:{line_number}: missing target {link}")

    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Checked {checked} entrypoint links.")


if __name__ == "__main__":
    main()
