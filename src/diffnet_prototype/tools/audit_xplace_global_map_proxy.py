#!/usr/bin/env python
"""Run the explicitly labelled global-map attribution proxy on a real Xplace map."""

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
for package_dir in (os.path.join(ROOT, "build", "dreamplace"), os.path.join(ROOT, "install", "dreamplace")):
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)

import torch
import dreamplace
for package_dir in (os.path.join(ROOT, "build", "dreamplace"), os.path.join(ROOT, "install", "dreamplace")):
    if package_dir not in dreamplace.__path__:
        dreamplace.__path__.append(package_dir)
import dreamplace.ops
for ops_dir in (os.path.join(ROOT, "build", "dreamplace", "ops"), os.path.join(ROOT, "install", "dreamplace", "ops")):
    if ops_dir not in dreamplace.ops.__path__:
        dreamplace.ops.__path__.append(ops_dir)
import dreamplace.ops.place_io
for place_io_dir in (os.path.join(ROOT, "build", "dreamplace", "ops", "place_io"), os.path.join(ROOT, "install", "dreamplace", "ops", "place_io")):
    if place_io_dir not in dreamplace.ops.place_io.__path__:
        dreamplace.ops.place_io.__path__.append(place_io_dir)
import Params
import PlaceDB
from dreamplace.global_map_attribution_proxy import endpoint_gradients_from_global_map
from dreamplace.placedb_two_pin import two_pin_pairs_from_flat_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("global_map")
    args = parser.parse_args()

    params = Params.Params()
    params.load(args.config)
    placedb = PlaceDB.PlaceDB()
    placedb(params)
    maps = torch.load(args.global_map, map_location="cpu")
    assert maps["provenance"] == "xplace-ggr-global-aggregate"
    assert maps["per_net_attribution_available"] is False

    pin_positions = torch.stack((
        torch.as_tensor(placedb.node_x[placedb.pin2node_map] + placedb.pin_offset_x),
        torch.as_tensor(placedb.node_y[placedb.pin2node_map] + placedb.pin_offset_y),
    )).float()
    pairs = two_pin_pairs_from_flat_map(
        torch.as_tensor(placedb.flat_net2pin_map),
        torch.as_tensor(placedb.flat_net2pin_start_map),
    )
    delta = pin_positions[:, pairs[:, 1]] - pin_positions[:, pairs[:, 0]]
    eligible = pairs[torch.linalg.vector_norm(delta, dim=0) > 0][:128]
    congestion = maps["congestion_overflow_2d"]
    result = endpoint_gradients_from_global_map(
        congestion,
        pin_positions,
        eligible,
        torch.tensor([placedb.routing_grid_xl, placedb.routing_grid_yl]),
        torch.tensor([placedb.routing_grid_size_x, placedb.routing_grid_size_y]),
        poisson_iterations=5,
        samples_per_segment=4,
    )
    gradients = result["endpoint_gradients"]
    print("source={} per_net_demand_available={}".format(
        result["attribution_source"], result["per_net_demand_available"]))
    print("map_shape={} real_two_pin_pairs={} eligible={} gradients={} hotspots={} finite={}".format(
        tuple(congestion.shape), pairs.shape[0], eligible.shape[0], tuple(gradients.shape),
        tuple(result["hotspot_indices"].shape), bool(torch.isfinite(gradients).all())))
    assert gradients.shape == (eligible.shape[0], 2, 2)
    assert torch.isfinite(gradients).all()
    print("real Xplace global-map attribution proxy smoke: PASS")


if __name__ == "__main__":
    main()
