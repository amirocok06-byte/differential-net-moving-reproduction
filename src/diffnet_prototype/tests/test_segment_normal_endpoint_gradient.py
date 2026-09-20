"""Synthetic tests for normal projection and virtual-cell endpoint attribution."""

import torch

from dreamplace.segment_normal_endpoint_gradient import (
    endpoint_gradients,
    project_gradient_to_normal,
    segment_tangent_normal,
)


def test_tangent_and_normal_are_orthonormal():
    tangent, normal = segment_tangent_normal(torch.tensor([1., 2.]), torch.tensor([4., 6.]))
    torch.testing.assert_close(torch.linalg.vector_norm(tangent), torch.tensor(1.))
    torch.testing.assert_close(torch.linalg.vector_norm(normal), torch.tensor(1.))
    torch.testing.assert_close(torch.dot(tangent, normal), torch.tensor(0.))


def test_projection_removes_tangential_component():
    start, end = torch.tensor([0., 0.]), torch.tensor([10., 0.])
    _, normal = segment_tangent_normal(start, end)
    torch.testing.assert_close(project_gradient_to_normal(torch.tensor([3., 4.]), normal), torch.tensor([0., 4.]))


def test_endpoint_attribution_matches_autograd():
    start = torch.tensor([1., 2.], dtype=torch.double, requires_grad=True)
    end = torch.tensor([5., 5.], dtype=torch.double, requires_grad=True)
    a = torch.tensor(0.25, dtype=torch.double)
    virtual = (1 - a) * start + a * end
    raw = torch.tensor([2., -3.], dtype=torch.double)
    _, normal = segment_tangent_normal(start.detach(), end.detach())
    projected = project_gradient_to_normal(raw, normal)
    objective = torch.dot(projected, virtual)
    grad_start, grad_end = torch.autograd.grad(objective, (start, end))
    _, expected_start, expected_end = endpoint_gradients(raw, start.detach(), end.detach(), a)
    torch.testing.assert_close(grad_start, expected_start)
    torch.testing.assert_close(grad_end, expected_end)


def test_endpoint_gradients_match_central_difference():
    start = torch.tensor([1.0, 2.0], dtype=torch.double)
    end = torch.tensor([5.0, 5.0], dtype=torch.double)
    raw = torch.tensor([2.0, -3.0], dtype=torch.double)
    attribution = 0.25
    _, grad_start, grad_end = endpoint_gradients(raw, start, end, attribution)
    _, normal = segment_tangent_normal(start, end)
    projected = project_gradient_to_normal(raw, normal)

    def objective(x, y):
        virtual = (1 - attribution) * x + attribution * y
        return torch.dot(projected, virtual)

    epsilon = 1e-6
    for endpoint, expected in ((start, grad_start), (end, grad_end)):
        numeric = []
        for axis in range(2):
            delta = torch.zeros(2, dtype=torch.double)
            delta[axis] = epsilon
            if endpoint is start:
                plus = objective(start + delta, end)
                minus = objective(start - delta, end)
            else:
                plus = objective(start, end + delta)
                minus = objective(start, end - delta)
            numeric.append((plus - minus) / (2 * epsilon))
        torch.testing.assert_close(torch.stack(numeric), expected, atol=1e-8, rtol=1e-8)
    torch.testing.assert_close(grad_start + grad_end, projected)


def test_degenerate_segment_is_rejected():
    try:
        segment_tangent_normal(torch.zeros(2), torch.zeros(2))
    except ValueError:
        return
    raise AssertionError("expected ValueError")


if __name__ == "__main__":
    test_tangent_and_normal_are_orthonormal()
    test_projection_removes_tangential_component()
    test_endpoint_attribution_matches_autograd()
    test_endpoint_gradients_match_central_difference()
    test_degenerate_segment_is_rejected()
    print("segment normal/endpoint gradient test: PASS")
