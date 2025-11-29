
import numpy as np
import cv2

import math
from typing import Optional, Tuple

def concatenate_images(*args, grid_shape : Optional[Tuple[int, int]] = None):

    if len(args) == 0:
        return np.array([])

    max_height = max([x.shape[0] for x in args])
    max_width = max([x.shape[1] for x in args])

    if len(args) == 1:
        return args[0]

    n_images = len(args)

    grid_width = 1
    while ((grid_width ** 2) < n_images):
        grid_width += 1

    grid_height = math.ceil(n_images / grid_width)

    if grid_shape is not None:
        grid_height, grid_width = grid_shape

    concatenated_image = np.zeros((max_height * grid_height,
                                   max_width * grid_width,
                                   3))

    max_y = 0
    max_x = 0

    def fill_output_at_grid_coordinate(grid_y, grid_x, new_image):

        tly, tlx = [max_height * grid_y, max_width * grid_x]
        bry, brx = [max_height * (grid_y+1), max_width * (grid_x+1)]

        if (len(new_image.shape) == 2):
            new_image = cv2.cvtColor(new_image.astype(np.float32), cv2.COLOR_GRAY2RGB)
        h, w = new_image.shape[:2]

        concatenated_image[tly:tly+h, tlx:tlx+w] = new_image

        nonlocal max_y, max_x

        max_y = max(max_y, tly + h)
        max_x = max(max_x, tlx + w)

    for i, img in enumerate(args):

        grid_y = i // grid_width
        grid_x = i % grid_width
        fill_output_at_grid_coordinate(grid_y, grid_x, img)

    concatenated_image = concatenated_image[:max_y, :max_x]

    return concatenated_image
