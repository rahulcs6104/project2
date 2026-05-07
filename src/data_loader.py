import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")

CATEGORY_FILES = {
    "cpu": "cpu",
    "gpu": "video-card",
    "motherboard": "motherboard",
    "ram": "memory",
    "storage": "internal-hard-drive",
    "psu": "power-supply",
    "case": "case",
}

REQUIRED_FIELDS = {
    "cpu": ["core_count", "boost_clock"],
    "gpu": ["chipset"],
    "motherboard": ["socket", "form_factor"],
    "ram": ["modules", "speed"],
    "storage": ["capacity", "type"],
    "psu": ["wattage", "efficiency"],
    "case": ["type"],
}


def _load_json(category):
    fname = os.path.join(DATA_DIR, CATEGORY_FILES[category] + ".json")
    with open(fname, "r") as f:
        return json.load(f)


def _has_required(item, category):
    for field in REQUIRED_FIELDS[category]:
        v = item.get(field)
        if v is None:
            return False
        if isinstance(v, (int, float)) and v <= 0:
            return False
    return True


def load_category(category):
    raw = _load_json(category)
    out = []
    for item in raw:
        price = item.get("price")
        if price is None or price <= 0:
            continue
        if not _has_required(item, category):
            continue
        item = dict(item)
        item["price_dollars"] = max(1, math.ceil(float(price)))
        item["category"] = category
        out.append(item)
    return out


def prune_dominated(items):
    if not items:
        return items
    sorted_items = sorted(items, key=lambda x: (x["price_dollars"], -x["score"]))
    kept = []
    best_score = -math.inf
    for it in sorted_items:
        if it["score"] > best_score:
            kept.append(it)
            best_score = it["score"]
    return kept


def load_all(categories=None):
    cats = categories or list(CATEGORY_FILES.keys())
    return {c: load_category(c) for c in cats}
