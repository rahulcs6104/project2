from flask import Flask, render_template, request

from src import optimizer, use_cases

app = Flask(__name__)


USE_CASE_LABELS = [
    ("gaming",  "Gaming",         "Esports, AAA, ray tracing. GPU heavy."),
    ("video",   "Video Editing",  "Timeline scrubs and encodes. CPU and RAM heavy."),
    ("aiml",    "AI / ML",        "Local training and inference. GPU and RAM."),
    ("general", "General Use",    "Browser, office, light dev. Balanced."),
]


@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        use_cases=USE_CASE_LABELS,
        budget=1500,
        selected_uc='gaming',
        build=None,
    )


@app.route('/build', methods=['POST'])
def build():
    try:
        budget = int(request.form.get('budget', '1500'))
    except ValueError:
        budget = 1500
    budget = max(300, min(budget, 10000))

    use_case = request.form.get('use_case', 'gaming')
    if use_case not in use_cases.WEIGHTS:
        use_case = 'gaming'

    result = optimizer.optimize(budget=budget, use_case=use_case)
    return render_template(
        "index.html",
        use_cases=USE_CASE_LABELS,
        budget=budget,
        selected_uc=use_case,
        build=result,
        weights=use_cases.WEIGHTS[use_case],
    )


@app.template_filter("part_spec")
def part_spec(item):
    if item is None:
        return ""
    cat = item["category"]
    if cat == "gpu":
        return item.get("chipset", "")
    if cat == "ram":
        m = item.get("modules") or []
        s = item.get("speed") or [None, "?"]
        if m:
            return f"{m[0]}×{m[1]}GB · DDR{s[0]}-{s[1]}"
    if cat == "storage":
        cap = item.get("capacity")
        t = item.get("type")
        t_str = "HDD" if isinstance(t, int) else (t or "")
        iface = item.get("interface", "")
        return f"{cap} GB · {t_str} · {iface}"
    if cat == "psu":
        return f"{item.get('wattage')}W · {item.get('efficiency', '')}"
    if cat == "cpu":
        return (
            f"{item.get('core_count')}C · {item.get('boost_clock')}GHz boost · "
            f"{item.get('microarchitecture') or '?'}"
        )
    if cat == "motherboard":
        return f"{item.get('socket', '')} · {item.get('form_factor', '')}"
    if cat == "case":
        return item.get("type", "")
    return ""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
