"""Number guard shared by the generators: a translated string must carry exactly the same numbers,
E-codes, percentages and URLs as its English string. Arabic may write 1 and 2 of a unit as words
(ساعتين، يوم واحد); those count as 1 and 2. Same rules as Keep or Toss (kot/translate.py)."""
from __future__ import annotations

import re
from collections import Counter

_AR_TWO = re.compile("(?:ساعت|يوم|أسبوع|شهر|سنت|مرت|دقيقت|درجت)(?:ين|ان)(?![ء-ي])")
_AR_ONE = re.compile("[ء-ي]+ (?:واحد|واحدة)(?![ء-ي])")
_URL = re.compile(r"https?://\S+")
_ECODE = re.compile(r"\bE ?(\d{3,4}[a-z]?)\b")
_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def tokens(text: str) -> Counter:
    text = _AR_ONE.sub(" 1 ", _AR_TWO.sub(" 2 ", text))
    c: Counter = Counter()
    for m in _URL.findall(text):
        c["url:" + m.rstrip(".,)")] += 1
    text = _URL.sub(" ", text)
    for m in _ECODE.findall(text):
        c["E" + m] += 1
    text = _ECODE.sub(" ", text)
    for m in _NUM.findall(text):
        c[m.replace(",", ".")] += 1
    if "%" in text:
        c["%"] = text.count("%")
    return c


def same(where: str, en: str, xx: str) -> None:
    if not isinstance(xx, str) or not xx.strip():
        raise ValueError(f"{where}: missing or empty")
    a, b = tokens(en), tokens(xx)
    if a != b:
        raise ValueError(f"{where}: numbers differ: {dict(a)} vs {dict(b)}")


def same_list(where: str, en: list, xx) -> None:
    if not isinstance(xx, list) or len(xx) != len(en):
        raise ValueError(f"{where}: {len(xx) if isinstance(xx, list) else 'no'} items, English has {len(en)}")
    for i, (a, b) in enumerate(zip(en, xx)):
        if isinstance(a, (list, tuple)):
            same_list(f"{where}[{i}]", list(a), list(b))
        else:
            same(f"{where}[{i}]", a, b)
