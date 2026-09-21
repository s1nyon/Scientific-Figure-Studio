import numpy as np
import pytest

from figure_studio.analysis import pareto_mask, running_best


def test_running_best_respects_maximization():
    np.testing.assert_allclose(
        running_best([1, 3, 2], goal="maximize"),
        [1, 3, 3],
    )


def test_running_best_rejects_unknown_goal():
    with pytest.raises(ValueError, match="minimize"):
        running_best([1, 2], goal="unknown")


def test_pareto_mask_uses_configured_objective_directions():
    values = np.array([[1, 3], [2, 2], [3, 1], [4, 4]])
    assert pareto_mask(values, ("minimize", "minimize")).tolist() == [True, True, True, False]


def test_pareto_mask_supports_mixed_directions_without_mutating_input():
    values = np.array([[1, 10], [2, 20], [3, 15]], dtype=float)
    original = values.copy()
    assert pareto_mask(values, ("minimize", "maximize")).tolist() == [True, True, False]
    np.testing.assert_array_equal(values, original)
