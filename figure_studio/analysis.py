"""Small, direction-aware numerical helpers for algorithm figures."""

from collections.abc import Iterable

import numpy as np


def _validate_goal(goal: str) -> None:
    if goal not in {"minimize", "maximize"}:
        raise ValueError("goal must be 'minimize' or 'maximize'")


def running_best(values: Iterable[float], goal: str = "minimize") -> np.ndarray:
    """Return the historical best value at every position."""

    _validate_goal(goal)
    array = np.asarray(list(values) if not isinstance(values, np.ndarray) else values, dtype=float)
    if array.ndim != 1:
        raise ValueError("values must be one-dimensional")
    if not np.isfinite(array).all():
        raise ValueError("values must contain only finite numbers")
    if goal == "minimize":
        return np.minimum.accumulate(array)
    return np.maximum.accumulate(array)


def pareto_mask(
    values: np.ndarray | Iterable[Iterable[float]],
    directions: Iterable[str] = ("minimize", "minimize"),
) -> np.ndarray:
    """Return a boolean mask for non-dominated rows under objective directions."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError("values must be a non-empty two-dimensional array")
    direction_tuple = tuple(directions)
    if len(direction_tuple) != array.shape[1]:
        raise ValueError("directions must have one entry per objective column")
    for direction in direction_tuple:
        _validate_goal(direction)
    if not np.isfinite(array).all():
        raise ValueError("values must contain only finite numbers")

    normalized = array.copy()
    for column, direction in enumerate(direction_tuple):
        if direction == "maximize":
            normalized[:, column] *= -1

    mask = np.ones(array.shape[0], dtype=bool)
    for row_index, row in enumerate(normalized):
        no_worse = np.all(normalized <= row, axis=1)
        strictly_better = np.any(normalized < row, axis=1)
        dominated = no_worse & strictly_better
        mask[row_index] = not np.any(dominated)
    return mask
