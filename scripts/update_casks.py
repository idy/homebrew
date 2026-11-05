#!/usr/bin/env python3
"""Update pinned casks from complete, stable GitHub releases."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = {
    "tailsplit": {
        "arm": "TailSplit_{version}_darwin_arm64.dmg",
        "intel": "TailSplit_{version}_darwin_amd64.dmg",
    },
    "nootify": {"sha256": "Nootify_{version}_aarch64.dmg"},
}
VERSION = r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"


def release_values(project, release):
    """Accept only exact release assets with GitHub-generated SHA-256 digests."""
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError(f"{project}: expected a published stable release")
    tag = release.get("tag_name", "")
    if not isinstance(tag, str) or not re.fullmatch(r"v" + VERSION, tag):
        raise ValueError(f"{project}: expected a vX.Y.Z release tag")
    version = tag[1:]
    checksums = {}
    for architecture, pattern in ASSETS[project].items():
        filename = pattern.format(version=version)
        matches = [asset for asset in release.get("assets", []) if asset.get("name") == filename]
        if len(matches) != 1:
            raise ValueError(f"{project}: expected exactly one {filename}")
        asset = matches[0]
        expected_url = f"https://github.com/idy/{project}/releases/download/{tag}/{filename}"
        if asset.get("browser_download_url") != expected_url:
            raise ValueError(f"{project}: unexpected download URL for {filename}")
        digest = asset.get("digest")
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"{project}: missing SHA-256 digest for {filename}")
        checksums[architecture] = digest.removeprefix("sha256:")
    return version, checksums


def update_content(project, content, release):
    version, checksums = release_values(project, release)
    versions = re.findall(r'^  version "(' + VERSION + r')"$', content, re.MULTILINE)
    if len(versions) != 1:
        raise ValueError(f"{project}: expected one pinned version stanza")
    current = versions[0][0]
    if tuple(map(int, version.split("."))) < tuple(map(int, current.split("."))):
        raise ValueError(f"{project}: refusing downgrade from {current} to {version}")

    updated = re.sub(r'^  version "[^"]+"$', f'  version "{version}"', content, flags=re.MULTILINE)
    for architecture, checksum in checksums.items():
        if architecture == "sha256":
            prefix = r"^  sha256 "
        elif architecture == "arm":
            prefix = r"^  sha256 arm: +"
        else:
            prefix = r"^ +intel: +"
        pattern = re.compile(r'(' + prefix + r'")[0-9a-f]{64}(")', re.MULTILINE)
        updated, count = pattern.subn(lambda match: match[1] + checksum + match[2], updated)
        if count != 1:
            raise ValueError(f"{project}: expected one {architecture} SHA-256 stanza")

    if version == current and updated != content:
        raise ValueError(f"{project}: release {version} changed checksums; review it manually")
    return updated


def latest_release(project):
    response = subprocess.run(
        ["gh", "api", f"repos/idy/{project}/releases/latest"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(response.stdout)


def update_projects(projects, check=False, root=ROOT):
    # Validate every selected release before writing anything. An incomplete
    # multi-architecture release must not publish a partial tap update.
    changes = []
    for project in projects:
        path = root / "Casks" / f"{project}.rb"
        content = path.read_text()
        updated = update_content(project, content, latest_release(project))
        if updated != content:
            changes.append((path, updated))
    for path, updated in changes:
        print(f"{'Outdated' if check else 'Updating'}: {path.name}")
        if not check:
            path.write_text(updated)
    if not changes:
        print("Casks already match the latest stable releases.")
    return bool(changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report pending updates without writing files")
    parser.add_argument("projects", nargs="*", help="Project names (default: all)")
    args = parser.parse_args()
    projects = args.projects or list(ASSETS)
    unknown = set(projects) - ASSETS.keys()
    if unknown:
        parser.error(f"unknown projects: {', '.join(sorted(unknown))}")
    try:
        changed = update_projects(projects, args.check)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Update failed: {error}", file=sys.stderr)
        return 1
    return int(args.check and changed)


if __name__ == "__main__":
    sys.exit(main())
