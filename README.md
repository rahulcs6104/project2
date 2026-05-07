# project2 — PC build optimizer (Knapsack)

Given a budget and a use case (gaming / video editing / AI/ML / general),
recommend a complete PC build.


This is basically a mutiple choice kanpsack problem
Knapsack -> pick exactly one part from each category (CPU, GPU,
motherboard, RAM, storage, PSU, case) to maximize a weighted performance
score subject to the budget.

## running it web UI

```
pip3 install flask   
python3 app.py
```

Open **http://127.0.0.1:5050** in your browser


## Project layout


main.py         ->    Command line entry point
app.py          ->    Flask web app
templates/index.html -> single-page form and results
src/
  data_loader.py  ->  loads and clean PCPartPicker JSON
  scoring.py      ->   fake performance score per category
  use_cases.py     -> use-case weight table
  knapsack.py      -> 0/1 knapsack and MCKP, both with backtracking
  optimizer.py    ->  ties it all together
data/raw/          -> the json file from pc partpicker

