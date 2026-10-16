"""Load the project data (provided; level 0).

The data directory is found from $SANAD_DATA, or as a folder named data/ in the
current directory or one of its parents.
"""
import json
import os
from pathlib import Path

LEVEL = 0
SPLITS = ("train", "dev", "test")


def data_dir():
    if os.environ.get("SANAD_DATA"):
        return Path(os.environ["SANAD_DATA"])
    for d in (Path.cwd(), *Path.cwd().parents):
        if (d / "data" / "tickets_train.jsonl").exists():
            return d / "data"
    raise FileNotFoundError("no data/tickets_train.jsonl here or above; set SANAD_DATA")


def _jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def tickets(split):
    """Tickets of one split as dicts: id, text, intent, variety, course, amount, faq."""
    if split not in SPLITS:
        raise ValueError(f"split must be one of {SPLITS}")
    if split == "test" and os.environ.get("SANAD_OPEN_TEST") != "1":
        raise PermissionError("the test split is opened once, at level 6: "
                              "set SANAD_OPEN_TEST=1 and record that you did")
    return _jsonl(data_dir() / f"tickets_{split}.jsonl")


def faq():
    """FAQ passages as dicts: id, intent, title, text_en, text_ar."""
    return _jsonl(data_dir() / "faq.jsonl")


def passage_text(p):
    """The searchable text of one passage: title, English, and Arabic."""
    return f"{p['title']} {p['text_en']} {p['text_ar']}"
