#!/usr/bin/env python
"""Real PlaceDB shape smoke for selected multi-pin cell moving."""

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "dreamplace"))
import dreamplace
for path in (os.path.join(ROOT, "build", "dreamplace"), os.path.join(ROOT, "install", "dreamplace")):
    dreamplace.__path__.append(path)
import dreamplace.ops
for path in (os.path.join(ROOT, "build", "dreamplace", "ops"), os.path.join(ROOT, "install", "dreamplace", "ops")):
    dreamplace.ops.__path__.append(path)
import dreamplace.ops.place_io
for path in (os.path.join(ROOT, "build", "dreamplace", "ops", "place_io"), os.path.join(ROOT, "install", "dreamplace", "ops", "place_io")):
    dreamplace.ops.place_io.__path__.append(path)

import torch
import Params
import PlaceDB
from dreamplace.selected_multi_pin import apply_selected_multi_pin_gradient
from dreamplace.selected_multi_pin_trace import build_selected_multi_pin_trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--trace-output", required=True)
    args = parser.parse_args()

    params = Params.Params()
    params.load(args.config)
    placedb = PlaceDB.PlaceDB()
    placedb(params)
    n = int(placedb.num_physical_nodes)
    pin2node = torch.as_tensor(placedb.pin2node_map, dtype=torch.long)
    pin_count = torch.bincount(pin2node, minlength=n).float()
    # Synthetic only: correlate the scalar with pin count so the selected
    # branch is exercised while preserving the real cell/pin tensor shapes.
    cell_congestion = 0.5 + 0.5 * pin_count / pin_count.max().clamp_min(1)
    baseline = torch.zeros((n, 2), dtype=torch.float32)
    congestion_gradient = torch.stack((cell_congestion, -cell_congestion), dim=1)
    selected_gradient, selected_mask = apply_selected_multi_pin_gradient(
        baseline, congestion_gradient, pin_count, cell_congestion)
    trace = build_selected_multi_pin_trace(
        pin_count=pin_count, cell_congestion=cell_congestion,
        baseline_gradient=baseline, congestion_gradient=congestion_gradient,
        selected_mask=selected_mask, selected_gradient=selected_gradient,
        provenance="mgc_fft_1-placedb-synthetic-cell-congestion")
    trace.update({
        "design_name": params.design_name(),
        "node_count": n,
        "pin_count_total": int(pin2node.numel()),
        "synthetic_input": True,
    })
    output = os.path.abspath(args.trace_output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    torch.save(trace, output)
    print("design={} cells={} pins={} selected={} mask_shape={} gradient_shape={} finite={} trace={}".format(
        params.design_name(), n, int(pin2node.numel()), int(selected_mask.sum()),
        tuple(selected_mask.shape), tuple(selected_gradient.shape),
        bool(torch.isfinite(selected_gradient).all()), output))
    print("selected multi-pin real metadata shape smoke: PASS")


if __name__ == "__main__":
    main()
