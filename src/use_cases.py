USE_CASES = ("gaming", "video", "aiml", "general")

WEIGHTS = {
    "gaming":  {"cpu": 0.20, "gpu": 0.40, "motherboard": 0.05,
                "ram": 0.10, "storage": 0.10, "psu": 0.07, "case": 0.03},
    "video":   {"cpu": 0.30, "gpu": 0.25, "motherboard": 0.05,
                "ram": 0.20, "storage": 0.12, "psu": 0.05, "case": 0.03},
    "aiml":    {"cpu": 0.20, "gpu": 0.45, "motherboard": 0.05,
                "ram": 0.18, "storage": 0.05, "psu": 0.05, "case": 0.02},
    "general": {"cpu": 0.25, "gpu": 0.10, "motherboard": 0.10,
                "ram": 0.20, "storage": 0.20, "psu": 0.10, "case": 0.05},
}


def weight(use_case, category):
    if use_case not in WEIGHTS:
        raise ValueError(
            f"Unknown use case {use_case!r}; expected one of {list(WEIGHTS)}"
        )
    return WEIGHTS[use_case][category]


for _uc, _w in WEIGHTS.items():
    _s = sum(_w.values())
    assert abs(_s - 1.0) < 1e-9, f"weights for {_uc} sum to {_s}, not 1.0"
