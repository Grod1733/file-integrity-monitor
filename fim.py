import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict

def hash_file(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def build_snapshot(directory: Path) -> Dict[str, str]:
    snapshot: Dict[str, str] = {}

    for path in directory.rglob("*"):
        if path.is_file():
            snapshot[str(path)] = hash_file(path)

    return snapshot

def save_baseline(snapshot: Dict[str, str], baseline_file: Path) -> None:
    with baseline_file.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=4)

def load_baseline(baseline_file: Path) -> Dict[str, str]:
    with baseline_file.open("r", encoding="utf-8") as f:
        return json.load(f)

def compare_snapshots(old: Dict[str, str], new: Dict[str, str]) -> None:
    old_files = set(old.keys())
    new_files = set(new.keys())

    added = new_files - old_files
    removed = old_files - new_files
    common = old_files & new_files

    changed = [file for file in common if old[file] != new[file]]

    print("\nFile Integrity Monitor Results")
    print("-" * 35)

    if added:
        print("\nAdded files:")
        for file in sorted(added):
            print(f"+ {file}")

    if removed:
        print("\nRemoved files:")
        for file in sorted(removed):
            print(f"- {file}")

    if changed:
        print("\nModified files:")
        for file in sorted(changed):
            print(f"* {file}")

    if not added and not removed and not changed:
        print("No changes detected.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Simple File Integrity Monitor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    baseline_parser = subparsers.add_parser("baseline", help="Create a baseline snapshot")
    baseline_parser.add_argument("directory", type=Path)
    baseline_parser.add_argument("baseline_file", type=Path)

    check_parser = subparsers.add_parser("check", help="Compare current files to baseline")
    check_parser.add_argument("directory", type=Path)
    check_parser.add_argument("baseline_file", type=Path)

    args = parser.parse_args()

    if args.command == "baseline":
        snapshot = build_snapshot(args.directory)
        save_baseline(snapshot, args.baseline_file)
        print(f"Baseline saved to {args.baseline_file}")

    elif args.command == "check":
        old_snapshot = load_baseline(args.baseline_file)
        new_snapshot = build_snapshot(args.directory)
        compare_snapshots(old_snapshot, new_snapshot)

if __name__ == "__main__":
    main()
