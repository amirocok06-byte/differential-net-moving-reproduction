import torch

from dreamplace.net_moving_trace import build_net_moving_trace, trace_row


def main():
    probe = {
        "hotspot_index": torch.tensor([2, 1]),
        "hotspot": torch.tensor([5.0, 3.0], requires_grad=True),
        "virtual_cell": torch.tensor([4.0, 2.5], requires_grad=True),
        "raw_gradient": torch.tensor([1.0, 2.0], requires_grad=True),
        "projected_gradient": torch.tensor([0.0, 2.0], requires_grad=True),
        "start_gradient": torch.tensor([0.0, 0.5], requires_grad=True),
        "end_gradient": torch.tensor([0.0, 1.5], requires_grad=True),
    }
    start = torch.tensor([1.0, 2.0], requires_grad=True)
    end = torch.tensor([7.0, 3.0], requires_grad=True)
    trace = build_net_moving_trace(
        probe, net_id=12, segment_start=start, segment_end=end,
        attribution=0.25, distance_scale=2.0,
    )
    assert trace["net_id"] == 12
    assert trace["attribution"] == 0.25
    assert trace["hotspot"].device.type == "cpu"
    assert not trace["hotspot"].requires_grad
    row = trace_row(trace)
    assert row["hotspot_index_x"] == 2 and row["hotspot_index_y"] == 1
    assert row["projected_gradient_1"] == 2.0
    try:
        build_net_moving_trace({}, segment_start=start, segment_end=end)
    except KeyError:
        pass
    else:
        raise AssertionError("missing fields must be rejected")
    print("net-moving trace schema test: PASS")


if __name__ == "__main__":
    main()
