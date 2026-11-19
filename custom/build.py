"""Assemble the customized subscription and its AdGuard rule-set."""

import hashlib
import os
import re
import sys
from configparser import ConfigParser
from pathlib import Path

from adguard import supplement
from merge import merge


def add_bilibili(config, bili):
    newline = "\r\n" if "\r\n" in config else "\n"
    scripts = newline.join(f"{k} = {v}" for k, v in bili["Script"].items()) + newline
    header = re.compile(r"^\[Script\][ \t]*\r?\n", re.M | re.I)
    if header.search(config):
        config = header.sub(lambda m: m[0] + scripts, config, count=1)
    else:
        config += newline + "[Script]" + newline + scripts
    mitm = re.search(r"(?im)^\[MITM\][ \t]*\r?\n([\s\S]*?)(?=^\[|\Z)", config)
    if not mitm:
        config += newline + "[MITM]" + newline
        start = end = len(config)
    else:
        start, end = mitm.span(1)
    body = config[start:end]
    for key, value in bili["MITM"].items():
        match = re.search(rf"(?im)^{key}[ \t]*=[ \t]*([^\r\n]*)", body)
        if key == "hostname" and match:
            hosts = [h.strip() for h in (match[1] + "," + value).split(",") if h.strip()]
            value = ", ".join(dict.fromkeys(hosts))
        line = f"{key} = {value}"
        if match:
            body = body[:match.start()] + line + body[match.end():]
        else:
            body = line + newline + body
    return config[:start] + body + config[end:]


def build(upstream, adguard, output_directory):
    root = Path(__file__).parent
    personal = (root / "rules.list").read_text(encoding="utf-8-sig")
    # Keep routing lines verbatim; ConfigParser handles only the named script/MITM keys.
    sections = (root / "bilibili.conf").read_text(encoding="utf-8").split("[Script]", 1)
    bili_rules = sections[0].split("[Rule]", 1)[1].strip()
    bili = ConfigParser(interpolation=None, delimiters=("=",))
    bili.optionxform = str
    bili.read_string("[Script]" + sections[1])

    local = personal.rstrip() + "\n" + bili_rules + "\n"
    config = upstream.read_bytes().decode("utf-8")
    upstream_rules = config.split("[Rule]", 1)[1].split("\n[", 1)[0]
    external, guarded = supplement(adguard.read_text(encoding="utf-8"), local + upstream_rules)
    repository = os.environ.get("GITHUB_REPOSITORY", "yihui-fu/Shadowrocket-ADBlock-Rules")
    digest = hashlib.sha256(external.encode()).hexdigest()[:16]
    url = f"https://raw.githubusercontent.com/{repository}/release/adguard-dns.list?v={digest}"
    rules = local + f"RULE-SET,{url},REJECT\n" + "\n".join(guarded)
    config = add_bilibili(merge(config, rules), bili)
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / "adguard-dns.list").write_bytes(external.encode())
    (output_directory / "customized.conf").write_bytes(config.encode())


if __name__ == "__main__":
    build(*(Path(arg) for arg in sys.argv[1:]))
