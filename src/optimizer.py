from dataclasses import dataclass

from . import compatibility, data_loader, scoring, use_cases
from .knapsack import Item, mckp

CATEGORIES = ("cpu", "gpu", "motherboard", "ram", "storage", "psu", "case")


@dataclass
class Pick:
    category: str
    item: object
    weighted_value: float


@dataclass
class Build:
    use_case: str
    budget: int
    picks: list
    total_price: int
    total_weighted_value: float
    warnings: list
    socket: str = None
    form_factor: str = None


def _prepare_groups(use_case):
    out = {}
    for cat in CATEGORIES:
        items = data_loader.load_category(cat)
        for it in items:
            it["score"] = scoring.score_item(it)
        items = data_loader.prune_dominated(items)
        scoring.normalize_scores(items)
        w = use_cases.weight(use_case, cat)
        for it in items:
            it["value"] = it["normalized_score"] * w
        out[cat] = items
    return out


def _items_to_groups(by_cat):
    return [
        [Item(weight=it["price_dollars"], value=it["value"], payload=it)
         for it in by_cat[cat]]
        for cat in CATEGORIES
    ]


def _psu_warning(picks):
    by_cat = {p.category: p.item for p in picks if p.item is not None}
    psu = by_cat.get("psu")
    if not psu:
        return None
    cpu_tdp = (by_cat.get("cpu") or {}).get("tdp") or 65
    gpu_tdp = 250 if by_cat.get("gpu") else 0
    rest = 100
    est = cpu_tdp + gpu_tdp + rest
    recommended = int(est * 1.4)
    if psu.get("wattage", 0) < recommended:
        return (
            f"PSU is {psu['wattage']}W but estimated load is ~{est}W "
            f"(recommended ≥ {recommended}W with headroom)"
        )
    return None


def _solve_for_config(by_cat, socket, form_factor, budget):
    NEG = float("-inf")
    filtered = compatibility.filter_for_config(by_cat, socket, form_factor)
    if any(not filtered[cat] for cat in CATEGORIES):
        return NEG, [], 0

    groups = _items_to_groups(filtered)
    value, picks_items = mckp(groups, budget)
    if any(p is None for p in picks_items):
        return NEG, [], 0

    pick_objs = []
    total_price = 0
    for cat, item in zip(CATEGORIES, picks_items):
        pick_objs.append(
            Pick(category=cat, item=item.payload, weighted_value=item.value)
        )
        total_price += item.weight
    return value, pick_objs, total_price


def optimize(budget, use_case):
    if use_case not in use_cases.WEIGHTS:
        raise ValueError(
            f"Unknown use case {use_case!r}; expected one of "
            f"{list(use_cases.WEIGHTS)}"
        )
    if budget <= 0:
        raise ValueError("budget must be positive")

    by_cat = _prepare_groups(use_case)

    best = None
    for socket, form_factor in compatibility.candidate_configs():
        value, picks, total = _solve_for_config(by_cat, socket, form_factor, budget)
        if value == float("-inf"):
            continue
        if best is None or value > best[0]:
            best = (value, picks, total, socket, form_factor)

    if best is None:
        return Build(
            use_case=use_case,
            budget=budget,
            picks=[Pick(category=c, item=None, weighted_value=0.0) for c in CATEGORIES],
            total_price=0,
            total_weighted_value=0.0,
            warnings=[
                "No compatible build fits the budget. Try raising the budget."
            ],
            socket=None,
            form_factor=None,
        )

    value, picks, total, socket, form_factor = best
    warnings = []
    psu_warn = _psu_warning(picks)
    if psu_warn:
        warnings.append(psu_warn)
    return Build(
        use_case=use_case,
        budget=budget,
        picks=picks,
        total_price=total,
        total_weighted_value=value,
        warnings=warnings,
        socket=socket,
        form_factor=form_factor,
    )


def format_build(build):
    lines = []
    lines.append(
        f"Recommended build for use_case={build.use_case!r}, budget=${build.budget}"
    )
    if build.socket:
        lines.append(f"Platform: {build.socket} · {build.form_factor}")
    lines.append("-" * 70)
    lines.append(f"{'Category':<13} {'Price':>7}  {'Score':>6}  Part")
    lines.append("-" * 70)
    for p in build.picks:
        if p.item is None:
            lines.append(f"{p.category:<13} {'-':>7}  {'-':>6}  (no item fits the budget)")
            continue
        price = p.item["price_dollars"]
        score = p.item["normalized_score"]
        name = p.item["name"]
        suffix = ""
        if p.category == "gpu" and p.item.get("chipset"):
            suffix = f"  [{p.item['chipset']}]"
        elif p.category == "ram" and p.item.get("modules"):
            m = p.item["modules"]
            speed = (p.item.get("speed") or [None, "?"])[1]
            suffix = f"  [{m[0]}x{m[1]}GB DDR{(p.item.get('speed') or [4])[0]}-{speed}]"
        elif p.category == "storage":
            cap = p.item.get("capacity")
            t = p.item.get("type")
            t_str = "HDD" if isinstance(t, int) else (t or "")
            suffix = f"  [{cap}GB {t_str}]"
        elif p.category == "psu" and p.item.get("wattage"):
            suffix = f"  [{p.item['wattage']}W]"
        elif p.category == "motherboard":
            suffix = f"  [{p.item.get('socket', '?')}, {p.item.get('form_factor', '?')}]"
        elif p.category == "cpu":
            suffix = f"  [{p.item.get('microarchitecture') or '?'}]"
        lines.append(f"{p.category:<13} ${price:>6}  {score:>6.1f}  {name}{suffix}")
    lines.append("-" * 70)
    lines.append(
        f"Total price: ${build.total_price} of ${build.budget} budget   "
        f"weighted score: {build.total_weighted_value:.2f}"
    )
    if build.warnings:
        lines.append("")
        lines.append("Notes:")
        for w in build.warnings:
            lines.append(f"  - {w}")
    return "\n".join(lines)
