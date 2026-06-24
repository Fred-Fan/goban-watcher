from copy import deepcopy

import cv2
import numpy as np
from cv2.typing import MatLike

from src import CELL_SIZE, SCREEN_SIZE
from src.utils.colors import Color


def default_corners(shape: tuple[int, int, int]) -> list[list[int]]:
    """Corners should be a square in the middle of the image."""
    assert len(shape) == 3, "Invalid shape"
    y, x, _ = shape

    left = x // 4
    right = x - x // 4
    top = y // 4
    bottom = y - y // 4
    return [[left, top], [right, top], [right, bottom], [left, bottom]]


def add_grid(frame: MatLike) -> MatLike:
    new_frame = deepcopy(frame)
    for i in range(0, SCREEN_SIZE, CELL_SIZE):
        cv2.line(new_frame, (i, 0), (i, SCREEN_SIZE), Color.GREEN.value)
        cv2.line(new_frame, (0, i), (SCREEN_SIZE, i), Color.GREEN.value)
    return new_frame


def blur_and_sharpen(img: MatLike) -> MatLike:
    blurred_image = cv2.GaussianBlur(img, (5, 5), 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(blurred_image, -1, kernel)


def get_perspective_transform_matrix(corners: list) -> np.ndarray:
    """
    Compute perspective transformation matrix from corners.
    Cache this result to avoid recomputing for every frame.

    Args:
        corners: List of 4 corner points [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

    Returns:
        Perspective transformation matrix
    """
    src_points = np.array(corners, dtype=np.float32).reshape(4, 2)
    dst_points = np.array(
        [[0, 0], [SCREEN_SIZE, 0], [SCREEN_SIZE, SCREEN_SIZE], [0, SCREEN_SIZE]],
        dtype=np.float32,
    )
    return cv2.getPerspectiveTransform(src_points, dst_points)


def convert_to_top_down(
    frame: MatLike, corners: list = None, matrix: np.ndarray = None
) -> MatLike:
    """
    Convert frame to top-down view using either corners or pre-computed matrix.

    Args:
        frame: Input frame
        corners: Corner points (if matrix not provided)
        matrix: Pre-computed transformation matrix (preferred for performance)

    Returns:
        Transformed frame
    """
    if matrix is None:
        if corners is None:
            raise ValueError("Either corners or matrix must be provided")
        matrix = get_perspective_transform_matrix(corners)

    new_shape = (SCREEN_SIZE, SCREEN_SIZE)
    return cv2.warpPerspective(frame, matrix, new_shape)
