"""Insert personal routing rules at the beginning of the upstream [Rule] section."""

import re
import sys
from pathlib import Path


def merge(upstream, personal):
    headers = list(re.finditer(r"^\[Rule\][ \t]*(\r?\n)", upstream, re.MULTILINE))
    if len(headers) != 1:
        raise ValueError("Expected one [Rule] section in the upstream configuration")
    header = headers[0]
    rules = re.split(r"^\[", upstream[header.end():], maxsplit=1, flags=re.MULTILINE)[0]
    if not re.search(r"^FINAL\s*,\s*[^\s,]+", rules, re.MULTILINE | re.IGNORECASE):
        raise ValueError("Upstream [Rule] section has no FINAL policy")

    lines = []
    for line in personal.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ";", "//")):
            continue
        if line.startswith("[") or "," not in line:
            raise ValueError(f"Expected a routing rule in custom/rules.list: {line}")
        lines.append(line + header.group(1))
    return upstream[:header.end()] + "".join(lines) + upstream[header.end():]


if __name__ == "__main__":
    upstream, personal, output = map(Path, sys.argv[1:])
    result = merge(upstream.read_bytes().decode("utf-8"), personal.read_text(encoding="utf-8-sig"))
    output.write_bytes(result.encode("utf-8"))
