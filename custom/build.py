"""Build the customized subscription with AdGuard DNS and Bilibili rules."""

import re
import sys
from configparser import ConfigParser
from pathlib import Path

from merge import merge


def set_adguard_dns(config):
    general = re.search(r"(?ims)^\[General\][ \t]*(\r?\n)(.*?)(?=^\[|\Z)", config)
    if not general:
        raise ValueError("Expected a [General] section in the upstream configuration")
    newline, settings = general.groups()
    settings = re.sub(
        r"(?im)^[ \t]*(?:dns-server|fallback-dns-server)[ \t]*=[^\r\n]*(?:\r?\n|$)",
        "",
        settings,
    )
    dns = newline.join((
        "dns-server = https://dns.adguard-dns.com/dns-query",
        "fallback-dns-server = tls://dns.adguard-dns.com",
        "",
    ))
    return config[:general.start(2)] + dns + settings + config[general.end(2):]


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


def build(upstream, output_directory):
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
    config = set_adguard_dns(config)
    config = add_bilibili(merge(config, local), bili)
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / "customized.conf").write_bytes(config.encode())


if __name__ == "__main__":
    build(*(Path(arg) for arg in sys.argv[1:]))
