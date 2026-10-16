"""Level 1: the evaluation harness (Book, Chapter 1).

Every later level is judged with these functions, so they come first. A
prediction of None means the router declined to choose a label; it counts as a
miss for the true class and as a false alarm for no class.

Level 1 students implement the Chapter 1 measures listed in STUDENT. The other
functions are supplied complete so that the reports work from the start:
f_beta, macro, micro, margin95, precision_at_k, and reciprocal_rank are taught
in Book Chapter 4 (classifier audit and ranked-list evaluation).
"""
import math
from collections import Counter

LEVEL = 1
STUDENT = ("accuracy", "confusion", "per_class", "majority_baseline")


def accuracy(gold, pred):
    """Fraction of items whose prediction equals the reference label."""
    if len(gold) == 0:
        raise ZeroDivisionError()

    return (sum(g == p for g, p in zip(gold, pred))) / len(gold)


def confusion(labels, gold, pred):
    """Matrix as a dict of dicts: m[reference][prediction] = count.

    Rows are reference labels, as in the book. A None prediction is counted in
    an extra column named None.
    """
    columns = list(labels) + [None]

    matrix = {}
    for g in labels:
        matrix[g] = {}
        for c in columns:
            matrix[g][c] = 0

    for g, p in zip(gold, pred):
        matrix[g][p] += 1

    return matrix




def per_class(labels, gold, pred):
    """{label: (precision, recall)}; a 0/0 ratio is None, never 0 or 1."""
    def ratio(numerator, denominator):
        if denominator == 0:
            return None
        return numerator / denominator

    result = {}
    for label in labels:
        tp, fp, fn = 0, 0, 0
        for g, p in zip(gold, pred):
            if p == label and g == label:
                tp += 1
            elif p == label and g != label:
                fp += 1
            elif p != label and g == label:
                fn += 1
        result[label] = (ratio(tp, tp + fp), ratio(tp, tp + fn))

    return result


def f_beta(p, r, beta=1.0):
    """(beta^2 + 1) P R / (beta^2 P + R); None if P or R is undefined; 0 if both are 0."""
    if p is None or r is None:
        return None
    b2 = beta * beta
    return 0.0 if p == r == 0 else (b2 + 1) * p * r / (b2 * p + r)


def macro(values, undefined="exclude"):
    """Mean over classes. undefined='exclude' drops None values; 'zero' counts them as 0."""
    if undefined == "zero":
        values = [0.0 if v is None else v for v in values]
    else:
        values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def micro(labels, gold, pred):
    """(precision, recall) from the pooled one-vs-rest counts.

    With one label per item they equal accuracy, unless some predictions are None:
    those add misses but no false alarms, so micro precision rises above recall.
    """
    tp = sum(g == p for g, p in zip(gold, pred) if p in labels)
    said = sum(p in labels for p in pred)
    return (tp / said if said else None, tp / len(gold))


def majority_baseline(train_labels):
    """The label a no-model baseline predicts: most frequent, ties broken alphabetically."""
    counts = Counter(train_labels)
    most = max(counts.values())
    return min(label for label, c in counts.items() if c == most)


def margin95(p, n):
    """Rough 95% margin of an accuracy p measured on n items: 2 sqrt(p(1-p)/n)."""
    return 2 * math.sqrt(p * (1 - p) / n)


def precision_at_k(ranked, relevant, k):
    """Fraction of the top k results that are relevant (missing places count as wrong)."""
    return sum(r in relevant for r in ranked[:k]) / k


def reciprocal_rank(ranked, relevant):
    """1 / rank of the first relevant result, or 0 if none is returned."""
    for i, r in enumerate(ranked, 1):
        if r in relevant:
            return 1 / i
    return 0.0


# --- Provided reports built from the functions above -----------------------

INTENTS = ("access", "assessment", "registration", "fees", "other")


def router_report(router, tickets):
    gold = [t["intent"] for t in tickets]
    pred = [router.predict(t["text"]) for t in tickets]
    pc = per_class(INTENTS, gold, pred)
    f1 = [f_beta(p, r) for p, r in pc.values()]
    by_variety = {}
    for v in sorted({t["variety"] for t in tickets}):
        idx = [i for i, t in enumerate(tickets) if t["variety"] == v]
        by_variety[v] = accuracy([gold[i] for i in idx], [pred[i] for i in idx])
    acc = accuracy(gold, pred)
    return {"n": len(tickets), "accuracy": acc, "margin95": margin95(acc, len(tickets)),
            "macro_f1": macro(f1, "zero"), "declined": sum(p is None for p in pred),
            "per_class": pc, "by_variety": by_variety, "pred": pred}


def search_report(search, tickets, k=3):
    ranked = [search.search(t["text"], k) for t in tickets]
    rel = [set(t["faq"]) for t in tickets]
    by_variety = {}
    for v in sorted({t["variety"] for t in tickets}):
        idx = [i for i, t in enumerate(tickets) if t["variety"] == v]
        by_variety[v] = sum(reciprocal_rank(ranked[i], rel[i]) for i in idx) / len(idx)
    return {"n": len(tickets), "k": k,
            "p_at_k": sum(precision_at_k(r, s, k) for r, s in zip(ranked, rel)) / len(tickets),
            "mrr": sum(reciprocal_rank(r, s) for r, s in zip(ranked, rel)) / len(tickets),
            "empty": sum(not r for r in ranked), "by_variety": by_variety, "ranked": ranked}


def keyboard_report(keyboard, tickets, k=3):
    """Predict every token of every ticket from the tokens before it.

    acc1 and acc@k count a target as found when it is the first suggestion or
    among the first k. Perplexity uses keyboard.prob over the same targets, so
    two keyboards are comparable only under the same tokenizer. unk is the
    fraction of targets outside the keyboard's training vocabulary.
    """
    hit1 = hitk = unk = n = 0
    logp = 0.0
    for t in tickets:
        tokens = keyboard.prep(t["text"])
        for i, target in enumerate(tokens):
            history = tokens[:i]
            s = keyboard.suggest(history, k)
            hit1 += bool(s) and s[0] == target
            hitk += target in s
            unk += target not in keyboard.vocab
            logp += math.log(keyboard.prob(history, target))
            n += 1
    return {"n": n, "acc1": hit1 / n, "acc3": hitk / n, "unk": unk / n,
            "ppl": math.exp(-logp / n)}
