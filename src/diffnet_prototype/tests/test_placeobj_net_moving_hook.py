import os
import sys
import glob

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "dreamplace"))
import dreamplace
dreamplace.__path__.extend([
    os.path.join(_ROOT, "build", "dreamplace"),
    os.path.join(_ROOT, "install", "dreamplace"),
])
import dreamplace.ops
dreamplace.ops.__path__.extend([
    os.path.join(_ROOT, "build", "dreamplace", "ops"),
    os.path.join(_ROOT, "install", "dreamplace", "ops"),
])
for _ops_package in glob.glob(os.path.join(_ROOT, "build", "dreamplace", "ops", "*")) + glob.glob(os.path.join(_ROOT, "install", "dreamplace", "ops", "*")):
    if os.path.isdir(_ops_package):
        _package_name = os.path.basename(_ops_package)
        try:
            _module = __import__("dreamplace.ops." + _package_name, fromlist=["*"])
            _module.__path__.append(_ops_package)
        except ModuleNotFoundError:
            pass
import PlaceObj


class _Ops:
    def wirelength_op(self, pos):
        return (pos ** 2).sum()

    def density_op(self, pos):
        return (pos * 0).sum()


class _DB:
    regions = []


def make_model():
    model = PlaceObj.PlaceObj.__new__(PlaceObj.PlaceObj)
    model.placedb = _DB()
    model.op_collections = _Ops()
    model.density_weight = torch.tensor([1.0])
    model.density_factor = 1.0
    model.density_quad_coeff = 2000
    model.density_weight_grad_precond = None
    model.init_density = None
    model.quad_penalty = False
    model.net_moving_objective = None
    model.selected_multi_pin_objective = None
    return model


def main():
    pos = torch.tensor([1.0, -2.0], requires_grad=True)
    model = make_model()
    baseline = model.obj_fn(pos)
    baseline.backward()
    baseline_grad = pos.grad.detach().clone()
    assert torch.allclose(baseline, torch.tensor(5.0))
    assert torch.allclose(baseline_grad, 2 * pos.detach())

    pos.grad = None
    model.set_net_moving_objective(lambda x: 3.0 * x[0] ** 2)
    enabled = model.obj_fn(pos)
    enabled.backward()
    assert torch.allclose(enabled, torch.tensor(8.0))
    assert torch.allclose(pos.grad, torch.tensor([8.0, -4.0]))

    model.set_net_moving_objective(None)
    assert model.net_moving_objective is None
    try:
        model.set_net_moving_objective(3)
    except TypeError:
        pass
    else:
        raise AssertionError("non-callable hook must be rejected")
    pos.grad = None
    model.set_selected_multi_pin_objective(lambda x: 2.0 * x[1] ** 2)
    selected = model.obj_fn(pos)
    selected.backward()
    assert torch.allclose(selected, torch.tensor(13.0))
    assert torch.allclose(pos.grad, torch.tensor([2.0, -12.0]))
    model.set_selected_multi_pin_objective(None)
    print("PlaceObj net-moving hook test: PASS")


if __name__ == "__main__":
    main()
