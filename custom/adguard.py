"""Build a Shadowrocket rule-set from host-level AdGuard rules missing upstream."""

import re
from collections import Counter, defaultdict
from fnmatch import fnmatchcase
from itertools import product

SOURCE = "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt"
MASK = re.compile(r"[\w.*-]+", re.ASCII)
# This AdGuard exception requires a URL fragment. A DNS hostname cannot match it.
URL_EXCEPTION = r"@@/\.(gif|jpe?g|png|webp)#(\/?.+)?(\/(ad)s?\/|\/ad-)/"


def predicates(mask):
    """Return (type, value) pairs for a hostname mask; empty means not translatable."""
    left = "||" if mask.startswith("||") else "|" if mask.startswith("|") else ""
    right = next((end for end in ("^|", "^", "|") if mask.endswith(end)), "")
    name = mask[len(left):].removesuffix(right).lower()
    if not MASK.fullmatch(name) or re.fullmatch(r"[\d.]+", name):
        return ()
    if "*" not in name:
        if left == "||" and right:
            return (("DOMAIN-SUFFIX", name),)
        if (left == "|" and right) or (not left and not right and not name.startswith(".")):
            return (("DOMAIN", name),)
    pattern = name if right else name + "*"
    if left == "||":
        variants = (pattern, "*." + pattern)
    else:
        variants = (pattern if left else "*" + pattern,)
    return tuple(("DOMAIN-WILDCARD", re.sub(r"\*+", "*", s)) for s in variants)


def tails(name):
    parts = name.split(".")
    return (".".join(parts[i:]) for i in range(len(parts)))


def bucket(predicate):
    """Last two fixed labels; glob rules without two fixed labels use the slow path."""
    text = predicate[1]
    labels = text.rsplit(".", 2)[-2:]
    return ".".join(labels) if len(labels) == 2 and "*" not in ".".join(labels) else ""


def globs(predicate):
    kind, name = predicate
    return (name, "*." + name) if kind == "DOMAIN-SUFFIX" else (name,)


def intersect(a, b):
    """Whether two host globs with literal characters and '*' have a common match."""
    if "*" not in a:
        return fnmatchcase(a, b)
    if "*" not in b:
        return fnmatchcase(b, a)
    todo, seen = [(0, 0)], set()
    while todo:
        i, j = todo.pop()
        if (i, j) in seen:
            continue
        seen.add((i, j))
        if i == len(a) and j == len(b):
            return True
        x, y = a[i:i + 1], b[j:j + 1]
        if x == "*":
            todo.append((i + 1, j))
        if y == "*":
            todo.append((i, j + 1))
        if x and y and (x == y or "*" in (x, y)):
            todo.append((i + (x != "*"), j + (y != "*")))
    return False


def supplement(text, existing):
    if "! Title: AdGuard DNS filter" not in text.splitlines()[:20]:
        raise ValueError("Missing AdGuard DNS filter header")
    raw = {s.strip() for s in text.splitlines() if s.strip() and not s.startswith(("!", "#"))}
    disabled = {s.removesuffix("$badfilter") for s in raw if s.endswith("$badfilter")}
    blocks, exceptions, stats = {}, {}, Counter()
    for source in sorted(raw):
        if source.endswith("$badfilter") or source in disabled:
            stats["disabled/directives"] += 1
            continue
        allow = source.startswith("@@")
        mask = source.removeprefix("@@")
        important = mask.endswith("$important")
        mask = mask.removesuffix("$important")
        if not allow and not mask.endswith(("^", "|")):
            # A DNS supplement can safely keep the complete-domain portion of a
            # legacy prefix such as ||example.org without claiming example.org.uk.
            if mask.startswith("||") and re.fullmatch(r"[\w-]+(?:\.[\w-]+)+", mask[2:], re.ASCII):
                mask += "^"
                stats["narrowed to a complete domain"] += 1
            elif not re.fullmatch(r"[\w-]+(?:\.[\w-]+)+", mask, re.ASCII):
                stats["non-host or open-ended mask"] += 1
                continue
        if not allow and mask.rstrip("^|").endswith("*"):
            stats["open-ended wildcard"] += 1
            continue
        items = predicates(mask)
        if not items:
            if allow and source != URL_EXCEPTION:
                raise ValueError(f"Unrecognized AdGuard exception: {source}")
            stats["other syntax or IP literals"] += 1
            continue
        target = exceptions if allow else blocks
        for item in items:
            target[item] = important or target.get(item, False)

    if not blocks:
        raise ValueError("AdGuard returned no host rules")
    excluded = defaultdict(list)
    for item in exceptions:
        excluded[bucket(item)].append(item)
    known = set()
    for line in existing.splitlines():
        fields = [x.strip() for x in line.split(",")]
        if len(fields) == 3 and fields[-1].upper() == "REJECT":
            known.add((fields[0].upper(), fields[1].lower()))
    known_suffix = {v for k, v in known if k == "DOMAIN-SUFFIX"}
    new_suffix = {v for (k, v) in blocks if k == "DOMAIN-SUFFIX"}
    normal, guarded = [], []
    for item, important in sorted(blocks.items()):
        kind, name = item
        # Only the fixed labels after a wildcard can prove suffix coverage.
        fixed = name.split("*")[-1].lstrip(".") if "*" in name else name
        labels = set(tails(fixed)) if fixed else set()
        if "*" in name and not name.endswith("." + fixed):
            labels.discard(fixed)
        if item in known or labels & known_suffix:
            stats["existing coverage"] += 1
            continue
        if not important and (labels - ({name} if kind == "DOMAIN-SUFFIX" else set())) & new_suffix:
            stats["covered by another AdGuard entry"] += 1
            continue
        key = bucket(item)
        candidates = excluded[key] + excluded[""] if key else exceptions
        guards = []
        for exc in candidates:
            if important and not exceptions[exc]:
                continue
            if item == exc or (exc[0] == "DOMAIN-SUFFIX" and exc[1] in labels):
                break
            if any(intersect(a, b) for a, b in product(globs(item), globs(exc))):
                guards.append(",".join(exc))
        else:
            term = ",".join(item)
            if guards:
                conditions = [f"({term})", *(f"(NOT,(({e})))" for e in sorted(guards))]
                guarded.append("AND,(" + ",".join(conditions) + "),REJECT")
            else:
                normal.append(term)
            continue
        stats["excepted"] += 1
    if not normal:
        raise ValueError("Empty AdGuard supplement")
    print(f"AdGuard: {len(normal)} rule-set entries, {len(guarded)} exception-aware rules; {dict(stats)}")
    header = (
        "# AdGuard DNS filter supplement for Shadowrocket\n"
        f"# Source: {SOURCE}\n"
        "# Converted by custom/adguard.py. License and source lists: "
        "https://github.com/AdguardTeam/AdGuardSDNSFilter\n"
    )
    return header + "\n".join(normal) + "\n", guarded
