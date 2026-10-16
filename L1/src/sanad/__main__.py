"""Command line (provided; level 0).

  python -m sanad route  "3ayez asagel NLP101 bokra"
  python -m sanad search "forgot my portal password"
  python -m sanad report            # every available version, dev split
  python -m sanad report --part router --split train
  python -m sanad release           # level 6: audit, open test once, model card
"""
import argparse

from sanad import data, evaluate as ev, registry
from sanad.pipeline import Pipeline

LEVEL = 0


def _try(build, *args):
    """Score a version, or return the stub message if part of it is not implemented."""
    try:
        return build(*args)
    except NotImplementedError as e:
        return str(e)


def _fmt(x):
    return "  -  " if x is None else f"{x:.3f}"


def report(pipe, split, parts):
    tickets = data.tickets(split)
    print(f"split={split}  n={len(tickets)}  normalize={pipe.parts['normalize']}  "
          f"tokenize={pipe.parts['tokenize']}")
    varieties = sorted({t["variety"] for t in tickets})
    if "router" in parts:
        print(f"\n{'router':16s} {'acc':>6s} {'±95%':>6s} {'macroF1':>8s} {'declined':>8s}  "
              + " ".join(f"{v:>7s}" for v in varieties))
        for v in registry.available("router"):
            r = _try(lambda: ev.router_report(pipe.router(v), tickets))
            if isinstance(r, str):
                print(f"{v:16s} not implemented yet ({r})")
                continue
            print(f"{v:16s} {_fmt(r['accuracy'])} {_fmt(r['margin95'])} {_fmt(r['macro_f1']):>8s} "
                  f"{r['declined']:8d}  " + " ".join(f"{_fmt(r['by_variety'][x]):>7s}" for x in varieties))
    if "search" in parts:
        print(f"\n{'search':16s} {'P@3':>6s} {'MRR':>6s} {'empty':>6s}  "
              + " ".join(f"{v:>7s}" for v in varieties) + "   (MRR by variety)")
        for v in registry.available("search"):
            s = _try(lambda: ev.search_report(pipe.search(v), tickets))
            if isinstance(s, str):
                print(f"{v:16s} not implemented yet ({s})")
                continue
            print(f"{v:16s} {_fmt(s['p_at_k'])} {_fmt(s['mrr'])} {s['empty']:6d}  "
                  + " ".join(f"{_fmt(s['by_variety'][x]):>7s}" for x in varieties))
    if "keyboard" in parts and "keyboard" in registry.PARTS:
        try:
            versions = registry.available("keyboard")
        except ModuleNotFoundError:
            versions = []
        if versions:
            print(f"\n{'keyboard':16s} {'acc@1':>6s} {'acc@3':>6s} {'PPL':>8s} {'unk':>6s}")
            for v in versions:
                k = _try(lambda: ev.keyboard_report(pipe.keyboard(v), tickets))
                if isinstance(k, str):
                    print(f"{v:16s} not implemented yet ({k})")
                    continue
                ppl = "  -  " if k["ppl"] is None else f"{k['ppl']:8.1f}"
                print(f"{v:16s} {_fmt(k['acc1'])} {_fmt(k['acc3'])} {ppl:>8s} {_fmt(k['unk'])}")
    try:
        from sanad.coverage import unknown_by_variety
        unk = _try(lambda: unknown_by_variety(pipe.prep, data.tickets("train"), tickets))
    except ModuleNotFoundError:
        unk = None
    if isinstance(unk, dict):
        print("\nunknown-token rate by variety: "
              + "  ".join(f"{v} {_fmt(r)}" for v, r in unk.items()))


def release(pipe):
    """Level 6: audit the fitted parts, open the test split once, write MODEL_CARD.md."""
    import os
    from datetime import datetime
    from pathlib import Path
    from sanad import release as rel
    problems = {p: toks for p, toks in rel.audit(pipe).items() if toks}
    if problems:
        for p, toks in problems.items():
            print(f"{p}: fitted on tokens outside train: {toks[:8]}")
        raise SystemExit("fix the leaky fit before you open the test split")
    if os.environ.get("SANAD_OPEN_TEST") != "1":
        raise SystemExit("audit passed. To release, run once with SANAD_OPEN_TEST=1.")
    dev = data.tickets("dev")
    dev_scores = {"router": ev.router_report(pipe.router(), dev),
                  "search": ev.search_report(pipe.search(), dev)}
    if pipe.parts.get("keyboard"):
        dev_scores["keyboard"] = ev.keyboard_report(pipe.keyboard(), dev)
    test_scores = rel.test_scores(pipe)
    Path("MODEL_CARD.md").write_text(rel.model_card(pipe.parts, dev_scores, test_scores))
    with open("RELEASE.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} test split opened; "
                f"parts={pipe.parts}\n")
    print("wrote MODEL_CARD.md; the test split opening is recorded in RELEASE.log")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sanad")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("route", "search", "suggest"):
        sub.add_parser(name).add_argument("text")
    rp = sub.add_parser("report")
    rp.add_argument("--split", default="dev", choices=data.SPLITS)
    rp.add_argument("--part", action="append", choices=("router", "search", "keyboard"))
    sub.add_parser("release")
    args = ap.parse_args(argv)
    pipe = Pipeline()
    if args.cmd == "route":
        from sanad import clarify, slots
        text = pipe.normalize(args.text)
        intent = pipe.router().predict(args.text)
        course, amount = slots.course(text), slots.amount(text)
        print(f"intent={intent}  course={course}  amount={amount}")
        print(clarify.reply(intent, course, args.text))
    elif args.cmd == "search":
        for pid in pipe.search().search(args.text):
            p = next(p for p in data.faq() if p["id"] == pid)
            print(f"{pid}  {p['title']}")
    elif args.cmd == "suggest":
        print(" | ".join(pipe.keyboard().suggest(pipe.prep(args.text), 3)))
    elif args.cmd == "release":
        release(pipe)
    else:
        report(pipe, args.split, args.part or ("router", "search", "keyboard"))


if __name__ == "__main__":
    main()
