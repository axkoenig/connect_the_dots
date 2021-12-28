from PIL import Image
import numpy as np
import itertools
import logging
import copy


class ConnectTheDots:
    def __init__(
        self, inpaint_start_and_end_pixels: bool, logger: logging.RootLogger
    ) -> None:
        self.inpaint_start_and_end_pixels = inpaint_start_and_end_pixels
        self.logger = logger
        self.logger.debug("Instantiated ConnectTheDots class.")

    def load_img(self, img_load_path: str) -> np.ndarray:
        img = Image.open(img_load_path)
        self.logger.info(f"Loaded image from path '{img_load_path}'.")
        return np.array(img)

    def save_img(self, img: np.ndarray, img_save_path: str) -> None:
        pil_img = Image.fromarray(img)
        pil_img.save(img_save_path)
        self.logger.info(f"Saved image to path '{img_save_path}'.")

    def get_point_coords(self, img: np.ndarray) -> np.ndarray:
        """
        Iterates over image in O(hw) and returns numpy array of point coordinates.
        """
        height = img.shape[0]
        width = img.shape[1]

        coords = []
        for h in range(height):
            for w in range(width):
                # save coord if any of rgb values is non-zero
                if np.any(img[h, w][:3] > 0):
                    coords.append([h, w])

        self.logger.debug(f"Found non-black pixels at locations: {coords}.")
        return np.array(coords)

    def draw_line(
        self,
        img: np.ndarray,
        coord_1: np.ndarray,
        coord_2: np.ndarray,
        line_color: np.ndarray,
        algorithm: str,
    ) -> np.ndarray:
        if np.all(np.abs(coord_1 - coord_2) <= 1):
            self.logger.warning(
                f"Both coordinates {coord_1} and {coord_2} are equal or adjacent - cannot draw line! Returning original image."
            )
            return img

        for c in [coord_1, coord_2]:
            img_bounds = np.array(img.shape[:2]) - 1
            if any(c > img_bounds) or any(c < np.array((0, 0))):
                raise IndexError(
                    f"Coordinate {c} is out of image bounds [(0,0), {img_bounds}]!"
                )

        # make sure coord_1 is left-most coordinate
        if coord_1[1] > coord_2[1]:
            coord_1, coord_2 = coord_2, coord_1

        # corner case: coordinates have same height coordinate, draw horizontal line directly
        if coord_1[0] == coord_2[0]:
            self.logger.debug(f"Drawing horizontal line from {coord_1} to {coord_2}.")
            img[coord_1[0], coord_1[1] + 1 : coord_2[1], 0:3] = line_color
            return img

        # corner case: coordinates have same width coordinate, draw vertical line directly
        if coord_1[1] == coord_2[1]:
            min_height = min(coord_1[0], coord_2[0])
            max_height = max(coord_1[0], coord_2[0])
            self.logger.debug("Drawing vertical line from {coord_1} to {coord_2}.")
            img[min_height + 1 : max_height, coord_1[1], 0:3] = line_color
            return img

        self.logger.debug(
            f"Drawing line from {coord_1} to {coord_2} with {algorithm} algorithm."
        )

        if algorithm == "naive":
            return self.draw_line_naive(img, coord_1, coord_2, line_color)
        elif algorithm == "bresenham":
            return self.draw_line_bresenham(img, coord_1, coord_2, line_color)
        else:
            raise ValueError(
                f"Unknown algorithm name '{algorithm}'. Returning original image."
            )

    def calc_slope(self, coord_1: np.ndarray, coord_2: np.ndarray) -> float:
        return (coord_2[0] - coord_1[0]) / (coord_2[1] - coord_1[1])

    def draw_line_naive(
        self,
        img: np.ndarray,
        coord_left: np.ndarray,
        coord_right: np.ndarray,
        line_color: np.ndarray,
    ) -> np.ndarray:
        """
        Connects two pixels in an image with a line. This method assumes that coord_left is the
        left-most coordinate.
        This is a simple algorithm based on the equation of a line. It is slow since it performs
        floating point multiplication in each iteration and it generates sparse results for very
        steep lines.
        """
        if coord_left[1] > coord_right[1]:
            raise ValueError(
                f"Coordinate coord_left is {coord_left} and must be left of coord_right {coord_right}"
            )

        m = self.calc_slope(coord_left, coord_right)
        x_offset_l = 0 if self.inpaint_start_and_end_pixels else 1
        x_offset_r = 1 if self.inpaint_start_and_end_pixels else 0

        for x in range(coord_left[1] + x_offset_l, coord_right[1] + x_offset_r):
            img[int(m * (x - coord_left[1]) + coord_left[0]), x, 0:3] = line_color

        self.logger.debug(
            f"Drew line with slope {m} from pixel {coord_left} to {coord_right}."
        )
        return img

    def draw_line_bresenham(
        self,
        img: np.ndarray,
        coord_1: np.ndarray,
        coord_2: np.ndarray,
        line_color: np.ndarray,
    ) -> np.ndarray:
        """
        Connects two pixels in an image with a line.
        This is a classic line-drawing algorithm based solely on integer arithmetic, which is
        fast to compute. Starting from one coordinate and depending on an error variable,
        either x or y is incremented and the current pixel is inpainted until the other
        coordinate is reached.
        This implementation is based on https://en.wikipedia.org/wiki/Bresenham's_line_algorithm .
        """

        # determine slope, step directions and error value
        dx = abs(coord_2[1] - coord_1[1])
        dy = -abs(coord_2[0] - coord_1[0])
        sx = 1 if coord_1[1] < coord_2[1] else -1
        sy = 1 if coord_1[0] < coord_2[0] else -1
        err = dx + dy

        # define run variables
        x = coord_1[1]
        y = coord_1[0]

        while True:
            # only inpait start and end pixels if desired
            if self.inpaint_start_and_end_pixels or [y, x] not in [
                list(coord_1),
                list(coord_2),
            ]:
                img[y, x, 0:3] = line_color

            e2 = 2 * err
            if y == coord_2[0] and x == coord_2[1]:
                break
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

        return img

    def connect_the_dots(
        self, img: np.ndarray, algorithm: str, line_color: np.ndarray
    ) -> np.ndarray:
        # make sure not to modify the original image
        img = copy.deepcopy(img)

        coords = self.get_point_coords(img)

        # iterate over all possible coordinate pairs
        for coord in itertools.combinations(coords, 2):
            img = self.draw_line(img, coord[0], coord[1], line_color, algorithm)
        return img

    def process_img(
        self,
        img_load_path: str,
        img_save_path: str,
        algorithm: str,
        line_color: np.ndarray,
    ) -> None:
        img = self.load_img(img_load_path)
        self.logger.info("Connecting the dots ...")
        img = self.connect_the_dots(img, algorithm, line_color)
        self.save_img(img, img_save_path)
        self.logger.info("Processing done!")
