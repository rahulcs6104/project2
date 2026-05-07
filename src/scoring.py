import math
import re

_MICROARCH_MULT = {
    "zen 5": 1.30,
    "zen 4": 1.18,
    "zen 3": 1.05,
    "zen 2": 0.95,
    "zen+": 0.85,
    "zen": 0.80,
    "raptor lake": 1.20,
    "alder lake": 1.10,
    "rocket lake": 0.95,
    "comet lake": 0.85,
    "coffee lake": 0.80,
    "arrow lake": 1.25,
    "meteor lake": 1.15,
}


def score_cpu(item):
    cores = item["core_count"]
    boost = item["boost_clock"]
    arch = (item.get("microarchitecture") or "").lower()
    mult = _MICROARCH_MULT.get(arch, 1.0)
    return cores * boost * mult


_GPU_FAMILY_BASE = [
    (re.compile(r"GeForce RTX 50\d0", re.I),  40000),
    (re.compile(r"GeForce RTX 40\d0", re.I),  30000),
    (re.compile(r"GeForce RTX 30\d0", re.I),  20000),
    (re.compile(r"GeForce RTX 20\d0", re.I),  12000),
    (re.compile(r"GeForce GTX 16\d0", re.I),   9000),
    (re.compile(r"GeForce GTX 10\d0", re.I),   7000),
    (re.compile(r"GeForce GTX 9\d0", re.I),    4500),
    (re.compile(r"Radeon RX 9\d{3}", re.I),   30000),
    (re.compile(r"Radeon RX 7\d{3}", re.I),   22000),
    (re.compile(r"Radeon RX 6\d{3}", re.I),   16000),
    (re.compile(r"Radeon RX 5\d{3}", re.I),    9500),
    (re.compile(r"Arc B\d{3}", re.I),         12000),
    (re.compile(r"Arc A\d{3}", re.I),          9000),
    (re.compile(r"Quadro RTX", re.I),         15000),
    (re.compile(r"Titan", re.I),              14000),
]

_TIER_MULT = {90: 1.00, 80: 0.78, 70: 0.55, 60: 0.35, 50: 0.20, 40: 0.12, 30: 0.07}


def _gpu_tier(chipset):
    tier_digit = None
    m = re.search(r"\b(?:RTX|GTX)\s+\d{2}(\d)\d\b", chipset, re.I)
    if m:
        tier_digit = int(m.group(1))
    if tier_digit is None:
        m = re.search(r"\bRX\s+\d(\d)\d{2}\b", chipset, re.I)
        if m:
            tier_digit = int(m.group(1))
    if tier_digit is None:
        m = re.search(r"\bArc\s+[AB](\d)\d{2}\b", chipset, re.I)
        if m:
            tier_digit = int(m.group(1))
    if tier_digit is None:
        return 30
    raw = tier_digit * 10
    return min(_TIER_MULT.keys(), key=lambda t: abs(t - raw))


def score_gpu(item):
    chipset = item["chipset"]
    base = 0.0
    for pat, val in _GPU_FAMILY_BASE:
        if pat.search(chipset):
            base = val
            break
    if base == 0.0:
        mem = item.get("memory") or 1
        boost = item.get("boost_clock") or item.get("core_clock") or 1000
        return mem * boost / 50.0

    tier = _gpu_tier(chipset)
    mult = _TIER_MULT.get(tier, 0.15)
    bump = 1.0
    if re.search(r"\bTi\b|XTX\b|SUPER\b", chipset, re.I):
        bump = 1.10
    return base * mult * bump


def score_motherboard(item):
    max_mem = item.get("max_memory") or 32
    slots = item.get("memory_slots") or 2
    return 10 + math.log2(max_mem) * 2 + slots * 0.5


def score_ram(item):
    modules = item.get("modules") or [2, 8]
    speed = item.get("speed") or [4, 3200]
    total_gb = modules[0] * modules[1]
    mhz = speed[1]
    return total_gb * (1.0 + mhz / 10000.0)


def score_storage(item):
    capacity = item.get("capacity") or 1
    raw_type = item.get("type")
    if isinstance(raw_type, int):
        drive_type = "HDD"
    else:
        drive_type = (raw_type or "").upper()
    interface = (item.get("interface") or "").upper()

    if drive_type == "SSD":
        type_mult = 5.0
    elif drive_type == "HYBRID":
        type_mult = 2.0
    else:
        type_mult = 1.0

    if "PCIE 5" in interface or "PCIE 4" in interface:
        iface_mult = 2.0
    elif "PCIE" in interface or "M.2" in interface:
        iface_mult = 1.5
    else:
        iface_mult = 1.0

    return math.log2(max(2, capacity)) * type_mult * iface_mult


_EFFICIENCY_MULT = {
    "titanium": 1.30,
    "platinum": 1.20,
    "gold": 1.10,
    "silver": 1.00,
    "bronze": 0.95,
    "white": 0.90,
    "standard": 0.85,
}


def score_psu(item):
    wattage = item.get("wattage") or 500
    eff = (item.get("efficiency") or "").lower()
    mult = 1.0
    for k, v in _EFFICIENCY_MULT.items():
        if k in eff:
            mult = v
            break
    return math.log2(wattage) * mult


def score_case(item):
    return 1.0


SCORERS = {
    "cpu": score_cpu,
    "gpu": score_gpu,
    "motherboard": score_motherboard,
    "ram": score_ram,
    "storage": score_storage,
    "psu": score_psu,
    "case": score_case,
}


def score_item(item):
    return SCORERS[item["category"]](item)


def normalize_scores(items):
    if not items:
        return
    scores = [it["score"] for it in items]
    lo, hi = min(scores), max(scores)
    if hi <= lo:
        for it in items:
            it["normalized_score"] = 50.0
        return
    span = hi - lo
    for it in items:
        it["normalized_score"] = 100.0 * (it["score"] - lo) / span
