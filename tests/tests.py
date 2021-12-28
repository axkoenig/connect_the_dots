import os
import unittest
import logging
from os.path import dirname, abspath, join

from connect_the_dots import connect_the_dots
import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ctd = connect_the_dots.ConnectTheDots(0, logger)

data_dir = join(dirname(dirname(abspath(__file__))), "data")
img_load_path = join(data_dir, "four_dots.png")

test_dir = join(dirname(abspath(__file__)), "output")
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

line_color = [255, 0, 0]


class Tests(unittest.TestCase):
    def test_load_img(self):
        img = ctd.load_img(img_load_path)
        self.assertIsNotNone(img)
        self.assertEqual(img.shape, (100, 100, 3))

    def test_save_img_png(self):
        img_name = "test_save.png"
        img_save_path = join(test_dir, img_name)
        img = np.random.rand(400, 400, 4) * 255
        ctd.save_img(img.astype("uint8"), img_save_path)
        self.assertTrue(img_name in os.listdir(test_dir))

    def test_save_img_jpg(self):
        img_name = "test_save.jpg"
        img_save_path = join(test_dir, img_name)
        img = np.random.rand(400, 400, 3) * 255
        ctd.save_img(img.astype("uint8"), img_save_path)
        self.assertTrue(img_name in os.listdir(test_dir))

    def test_get_point_coords(self):
        test_coords = np.array([[22, 44], [40, 55], [66, 99], [0, 0]])

        # generate black image with randomly colored dots
        img = np.zeros((100, 100, 3), "uint8")
        for c in test_coords:
            img[c[0], c[1]] = np.random.rand(3) * 255

        coords = ctd.get_point_coords(img)
        self.assertTrue(np.array_equal(test_coords.sort(axis=0), coords.sort(axis=0)))

    def test_draw_line_horizontal(self):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([5, 90])
        coord_2 = np.array([5, 10])
        img[coord_1[0], coord_1[1]] = np.random.rand(3) * 255
        img[coord_2[0], coord_2[1]] = np.random.rand(3) * 255
        ctd.save_img(img, join(test_dir, "test_draw_line_horizontal_before.png"))
        img = ctd.draw_line(img, coord_1, coord_2, line_color, "naive")
        ctd.save_img(img, join(test_dir, "test_draw_line_horizontal_after.png"))

    def test_draw_line_vertical(self):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([50, 10])
        coord_2 = np.array([5, 10])
        img[coord_1[0], coord_1[1]] = np.random.rand(3) * 255
        img[coord_2[0], coord_2[1]] = np.random.rand(3) * 255
        ctd.save_img(img, join(test_dir, "test_draw_line_vertical_before.png"))
        img = ctd.draw_line(img, coord_1, coord_2, line_color, "naive")
        ctd.save_img(img, join(test_dir, "test_draw_line_vertical_after.png"))

    def test_draw_line_same_or_adjacent(self):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([50, 10])
        coord_2 = np.array([50, 10])
        new_img = ctd.draw_line(img, coord_1, coord_2, line_color, "naive")
        self.assertTrue(np.array_equal(img, new_img))

        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([51, 10])
        coord_2 = np.array([50, 10])
        new_img = ctd.draw_line(img, coord_1, coord_2, line_color, "naive")
        self.assertTrue(np.array_equal(img, new_img))

    def test_draw_line_unknown_algorithm(self):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([66, 6])
        coord_2 = np.array([6, 66])
        with self.assertRaises(ValueError):
            ctd.draw_line(img, coord_1, coord_2, line_color, "xxx")

    def test_draw_line_out_of_bounds(self):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([500, 10])
        coord_2 = np.array([50, 10])
        with self.assertRaises(IndexError):
            ctd.draw_line(img, coord_1, coord_2, line_color, "naive")

        coord_1 = np.array([0, 99])
        coord_2 = np.array([50, 109])
        with self.assertRaises(IndexError):
            ctd.draw_line(img, coord_1, coord_2, line_color, "naive")

        coord_1 = np.array([0, -1])
        coord_2 = np.array([50, 10])
        with self.assertRaises(IndexError):
            ctd.draw_line(img, coord_1, coord_2, line_color, "naive")

    def test_calc_slope(self):
        coord_1 = np.array([10, 0])
        coord_2 = np.array([0, 10])
        self.assertEqual(ctd.calc_slope(coord_1, coord_2), -1)

    def draw_line_diagonal_up(self, algorithm):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([50, 10])
        coord_2 = np.array([5, 88])
        img[coord_1[0], coord_1[1]] = np.random.rand(3) * 255
        img[coord_2[0], coord_2[1]] = np.random.rand(3) * 255
        ctd.save_img(
            img, join(test_dir, f"test_draw_line_diagonal_up_{algorithm}_before.png")
        )
        img = ctd.draw_line(img, coord_1, coord_2, line_color, "naive")
        ctd.save_img(
            img, join(test_dir, f"test_draw_line_diagonal_up_{algorithm}_after.png")
        )

    def draw_line_diagonal_down(self, algorithm):
        img = np.zeros((100, 100, 3), "uint8")
        coord_1 = np.array([4, 4])
        coord_2 = np.array([44, 44])
        img[coord_1[0], coord_1[1]] = np.random.rand(3) * 255
        img[coord_2[0], coord_2[1]] = np.random.rand(3) * 255
        ctd.save_img(
            img, join(test_dir, f"test_draw_line_diagonal_down_{algorithm}_before.png")
        )
        img = ctd.draw_line(img, coord_1, coord_2, line_color, algorithm)
        ctd.save_img(
            img, join(test_dir, f"test_draw_line_diagonal_down_{algorithm}_after.png")
        )

    def connect_the_dots(self, algorithm):
        img = np.zeros((100, 100, 3), "uint8")
        img[32, 2] = np.random.rand(3) * 255
        img[44, 22] = np.random.rand(3) * 255
        img[5, 16] = np.random.rand(3) * 255
        img[10, 90] = np.random.rand(3) * 255
        img[83, 40] = np.random.rand(3) * 255
        ctd.save_img(
            img, join(test_dir, f"test_connect_the_dots_{algorithm}_before.png")
        )
        img = ctd.connect_the_dots(img, algorithm, line_color)
        ctd.save_img(
            img, join(test_dir, f"test_connect_the_dots_{algorithm}_after.png")
        )

    def test_draw_line_diagonal_down_naive(self):
        self.draw_line_diagonal_down("naive")

    def test_draw_line_diagonal_down_bresenham(self):
        self.draw_line_diagonal_down("bresenham")

    def test_draw_line_diagonal_up_naive(self):
        self.draw_line_diagonal_up("naive")

    def test_draw_line_diagonal_up_bresenham(self):
        self.draw_line_diagonal_up("bresenham")

    def test_connect_the_dots_naive(self):
        self.connect_the_dots("naive")

    def test_connect_the_dots_bresenham(self):
        self.connect_the_dots("bresenham")


def remove_old_test_files():
    print(f"Removing all previously generated test files from '{test_dir}' directory.")
    for file_name in os.listdir(test_dir):
        if file_name.startswith("test"):
            file_path = join(test_dir, file_name)
            print(f"Removing '{file_path}'.")
            os.remove(file_path)
    print("----------------------------------------------------------------------")


if __name__ == "__main__":
    remove_old_test_files()
    unittest.main()
