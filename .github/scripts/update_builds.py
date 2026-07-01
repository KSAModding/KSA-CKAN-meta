#!/usr/bin/env python3
"""Append the latest KSA production version to builds.json.

Consumes the KSA master server's /version response (passed as argv[1]) and, if it
reports a plain year.month.build.revision version that is not already listed,
appends it to builds.json in the file's existing format. Prints the added version
to stdout on success and nothing otherwise, so the workflow can tell whether to
commit.
"""
import json
import re
import sys

BUILDS_FILE = "builds.json"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")


def main():
    if len(sys.argv) < 2:
        return
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Could not parse master-server response as JSON.", file=sys.stderr)
        return

    version = (payload.get("Version") or "").strip()
    if not VERSION_RE.match(version):
        print(f"Ignoring non-production version '{version}'.", file=sys.stderr)
        return

    with open(BUILDS_FILE, encoding="utf-8") as f:
        builds = json.load(f)

    if version in builds:
        print(f"Version '{version}' already present.", file=sys.stderr)
        return

    builds.append(version)
    with open(BUILDS_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n")
        f.write(",\n".join('    "%s"' % b for b in builds))
        f.write("\n]\n")

    # stdout is the added version, consumed by the workflow to decide on committing
    print(version)


if __name__ == "__main__":
    main()
