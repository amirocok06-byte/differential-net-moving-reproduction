#!/usr/bin/env python
"""Audit the paper-method code-location acceptance items without running placement."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def contains(path, text):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return text in handle.read()


def main():
    checks = {
        "objective hook": contains("dreamplace/PlaceObj.py", "self.net_moving_objective") and contains("dreamplace/PlaceObj.py", "result = result + self.net_moving_objective(pos)"),
        "NonLinearPlace installer": contains("dreamplace/NonLinearPlace.py", 'getattr(params, "net_moving_objective", None)') and contains("dreamplace/NonLinearPlace.py", "model.set_net_moving_objective(objective_fn)"),
        "snapshot factory": contains("dreamplace/net_moving_callback.py", "make_two_pin_objective_from_congestion_snapshot"),
        "real pair extraction": contains("dreamplace/placedb_two_pin.py", "two_pin_pairs_from_flat_map"),
        "trace schema": contains("dreamplace/net_moving_trace.py", "build_net_moving_trace") and contains("dreamplace/net_moving_trace.py", "trace_row"),
        "default-off test": os.path.exists(os.path.join(ROOT, "test/test_placeobj_net_moving_hook.py")),
        "main-flow smoke": os.path.exists(os.path.join(ROOT, "tools/synthetic_nonlinearplace_smoke.py")),
        "selected multi-pin hook": contains("dreamplace/PlaceObj.py", "selected_multi_pin_objective") and contains("dreamplace/NonLinearPlace.py", "set_selected_multi_pin_objective"),
        "selected multi-pin trace": contains("dreamplace/selected_multi_pin_trace.py", "build_selected_multi_pin_trace") and os.path.exists(os.path.join(ROOT, "test/test_selected_multi_pin_trace.py")),
    }
    for name, passed in checks.items():
        print("{}: {}".format(name, "PASS" if passed else "FAIL"))
    if not all(checks.values()):
        raise SystemExit(1)
    print("method target structural audit: PASS")


if __name__ == "__main__":
    main()
