SUPPORTED_SOCKETS = ("AM5", "AM4", "LGA1700", "LGA1851", "LGA1200", "LGA1151")

ARCH_TO_SOCKET = {
    "zen 5": "AM5",
    "zen 4": "AM5",
    "zen 3": "AM4",
    "zen 2": "AM4",
    "zen+": "AM4",
    "zen": "AM4",
    "arrow lake": "LGA1851",
    "raptor lake": "LGA1700",
    "raptor lake refresh": "LGA1700",
    "alder lake": "LGA1700",
    "rocket lake": "LGA1200",
    "comet lake": "LGA1200",
    "coffee lake": "LGA1151",
    "coffee lake refresh": "LGA1151",
}


def cpu_socket(cpu):
    arch = (cpu.get("microarchitecture") or "").lower()
    return ARCH_TO_SOCKET.get(arch)


DDR_BY_SOCKET = {
    "AM5": {5},
    "AM4": {4},
    "LGA1700": {4, 5},
    "LGA1851": {5},
    "LGA1200": {4},
    "LGA1151": {4},
}


def ram_compatible(ram, socket):
    speed = ram.get("speed") or [4, 0]
    gen = speed[0]
    return gen in DDR_BY_SOCKET.get(socket, set())


SIZE_ORDER = {
    "mini itx": 1,
    "miniitx": 1,
    "mini dtx": 1,
    "thin mini itx": 1,
    "micro atx": 2,
    "microatx": 2,
    "atx": 3,
    "ssi ceb": 3,
    "eatx": 4,
    "e-atx": 4,
    "xl atx": 5,
}


def _size_from_string(s):
    if not s:
        return 0
    s_low = s.lower()
    for token in ("xl atx", "thin mini itx", "mini itx", "miniitx", "mini dtx",
                  "eatx", "e-atx", "ssi ceb", "micro atx", "microatx", "atx"):
        if token in s_low:
            return SIZE_ORDER[token]
    return 0


def mobo_size(motherboard):
    return _size_from_string(motherboard.get("form_factor") or "")


def case_max_size(case):
    return _size_from_string(case.get("type") or "")


def case_fits_form_factor(case, form_factor):
    needed = _size_from_string(form_factor)
    have = case_max_size(case)
    if needed == 0 or have == 0:
        return False
    return have >= needed


def filter_for_config(items_by_cat, socket, form_factor):
    out = {}
    out["cpu"] = [c for c in items_by_cat["cpu"] if cpu_socket(c) == socket]
    out["motherboard"] = [
        m for m in items_by_cat["motherboard"]
        if m.get("socket") == socket and (m.get("form_factor") or "") == form_factor
    ]
    out["ram"] = [r for r in items_by_cat["ram"] if ram_compatible(r, socket)]
    out["case"] = [
        c for c in items_by_cat["case"] if case_fits_form_factor(c, form_factor)
    ]
    out["gpu"] = items_by_cat["gpu"]
    out["storage"] = items_by_cat["storage"]
    out["psu"] = items_by_cat["psu"]
    return out


def candidate_configs():
    form_factors = ("ATX", "Micro ATX", "Mini ITX")
    return [(s, ff) for s in SUPPORTED_SOCKETS for ff in form_factors]
