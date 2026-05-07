from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    weight: int
    value: float
    payload: object = None


def knapsack_01(items, capacity):
    n = len(items)
    if n == 0 or capacity <= 0:
        return 0.0, []

    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wi = items[i - 1].weight
        vi = items[i - 1].value
        for w in range(capacity + 1):
            best = dp[i - 1][w]
            if wi <= w:
                cand = dp[i - 1][w - wi] + vi
                if cand > best:
                    best = cand
            dp[i][w] = best

    chosen = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(items[i - 1])
            w -= items[i - 1].weight
    chosen.reverse()
    return dp[n][capacity], chosen


def mckp(groups, capacity):
    g = len(groups)
    NEG = float("-inf")

    dp = [[NEG] * (capacity + 1) for _ in range(g + 1)]
    choice = [[-1] * (capacity + 1) for _ in range(g + 1)]

    for w in range(capacity + 1):
        dp[0][w] = 0.0

    for i in range(1, g + 1):
        group = groups[i - 1]
        prev = dp[i - 1]
        for w in range(capacity + 1):
            best = NEG
            best_j = -1
            for j, item in enumerate(group):
                if item.weight <= w and prev[w - item.weight] != NEG:
                    cand = prev[w - item.weight] + item.value
                    if cand > best:
                        best = cand
                        best_j = j
            dp[i][w] = best
            choice[i][w] = best_j

    best_w = 0
    best_val = NEG
    for w in range(capacity + 1):
        if dp[g][w] > best_val:
            best_val = dp[g][w]
            best_w = w

    if best_val == NEG:
        return 0.0, [None] * g

    picks = [None] * g
    w = best_w
    for i in range(g, 0, -1):
        j = choice[i][w]
        if j == -1:
            picks[i - 1] = None
        else:
            item = groups[i - 1][j]
            picks[i - 1] = item
            w -= item.weight
    return best_val, picks
