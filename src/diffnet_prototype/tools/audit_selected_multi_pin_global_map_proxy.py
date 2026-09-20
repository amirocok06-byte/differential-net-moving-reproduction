#!/usr/bin/env python
"""Project a real Xplace global map onto DREAMPlace cells for a proxy smoke."""

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
from dreamplace.paper_congestion import congestion_map, potential_gradient_neumann, poisson_source, solve_poisson_neumann_jacobi
from dreamplace.selected_multi_pin import apply_selected_multi_pin_gradient
from dreamplace.selected_multi_pin_trace import build_selected_multi_pin_trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("global_map")
    parser.add_argument("--trace-output", required=True)
    args = parser.parse_args()
    params = Params.Params()
    params.load(args.config)
    placedb = PlaceDB.PlaceDB()
    placedb(params)
    maps = torch.load(args.global_map, map_location="cpu")
    demand, capacity = maps["demand_2d"].float(), maps["capacity_2d"].float()
    overflow = congestion_map(demand, capacity)
    grid_size = torch.tensor([placedb.routing_grid_size_x, placedb.routing_grid_size_y])
    phi = solve_poisson_neumann_jacobi(poisson_source(demand, capacity), grid_size, iterations=5)
    gx, gy = potential_gradient_neumann(phi, grid_size)
    n = int(placedb.num_physical_nodes)
    pin2node = torch.as_tensor(placedb.pin2node_map, dtype=torch.long)
    pin_count = torch.bincount(pin2node, minlength=n).float()
    x = torch.as_tensor(placedb.node_x[:n], dtype=torch.float32)
    y = torch.as_tensor(placedb.node_y[:n], dtype=torch.float32)
    ix = torch.floor((x - float(placedb.routing_grid_xl)) / grid_size[0]).long().clamp(0, overflow.shape[1] - 1)
    iy = torch.floor((y - float(placedb.routing_grid_yl)) / grid_size[1]).long().clamp(0, overflow.shape[0] - 1)
    cell_congestion = overflow[iy, ix]
    congestion_gradient = torch.stack((gx[iy, ix], gy[iy, ix]), dim=1)
    baseline_gradient = torch.zeros_like(congestion_gradient)
    selected_gradient, selected_mask = apply_selected_multi_pin_gradient(
        baseline_gradient, congestion_gradient, pin_count, cell_congestion)
    trace = build_selected_multi_pin_trace(
        pin_count=pin_count, cell_congestion=cell_congestion,
        baseline_gradient=baseline_gradient, congestion_gradient=congestion_gradient,
        selected_mask=selected_mask, selected_gradient=selected_gradient,
        provenance="xplace-ggr-global-aggregate-cell-projection")
    trace.update({
        "design_name": params.design_name(),
        "node_count": n,
        "pin_count_total": int(pin2node.numel()),
        "map_shape": tuple(overflow.shape),
        "map_provenance": maps.get("provenance", "unknown"),
        "per_net_attribution_available": False,
        "synthetic_input": False,
    })
    output = os.path.abspath(args.trace_output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    torch.save(trace, output)
    print("design={} cells={} pins={} map={} selected={} gradient={} finite={} provenance={}".format(
        params.design_name(), n, int(pin2node.numel()), tuple(overflow.shape), int(selected_mask.sum()),
        tuple(selected_gradient.shape), bool(torch.isfinite(selected_gradient).all()), trace["provenance"]))
    print("selected multi-pin global-map proxy smoke: PASS")


if __name__ == "__main__":
    main()
