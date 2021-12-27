import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

from connect_the_dots import connect_the_dots


def parse_args():
    parser = argparse.ArgumentParser(
        "Connects coloured dots on a black image with white lines."
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data",
        help="data directory for input and output images.",
    )
    parser.add_argument(
        "--img_name",
        type=str,
        default="three_dots.png",
        help="name of image file in data directory.",
    )
    parser.add_argument(
        "--logs_dir",
        type=str,
        default="logs",
        help="log directory.",
    )
    parser.add_argument(
        "--log_name",
        type=str,
        default="test",
        help="name of the log file (date and time will be added).",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="bresenham",
        help="name of the algorithm (either 'naive' or 'bresenham').",
    )
    parser.add_argument(
        "--line_color",
        nargs="+",
        default=[255, 255, 255],
        help="color of the connecting lines expressed in [r,g,b] format.",
    )
    parser.add_argument(
        "--inpaint_start_and_end_pixels",
        type=int,
        default=0,
        help="Whether to inpaint start and end pixels with line color.",
    )
    args = parser.parse_args()

    if args.inpaint_start_and_end_pixels not in [0, 1]:
        raise ValueError(
            f"Argument inpaint_start_and_end_pixels must be 0 or 1, you passed {args.inpaint_start_and_end_pixels}."
        )
    return args


def setup_logger(args):

    logFormatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s]  %(message)s"
    )
    logger = logging.getLogger("ConnectTheDots")
    logger.setLevel(logging.DEBUG)

    # ensure log file is saved to disk
    if not os.path.exists(args.logs_dir):
        os.makedirs(args.logs_dir)
    now = datetime.now()
    fileHandler = logging.FileHandler(
        f"{args.logs_dir}/{args.log_name}_" + now.strftime("%m-%d-%Y_%H:%M:%S")
    )
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    # pipe logs to the console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    return logger


if __name__ == "__main__":
    args = parse_args()
    logger = setup_logger(args)
    logger.info("Starting program.")

    ctd = connect_the_dots.ConnectTheDots(args.inpaint_start_and_end_pixels, logger)

    # specify load and save paths
    img_load_path = os.path.join(args.data_dir, args.img_name)
    path = Path(img_load_path)
    img_save_path = path.with_name(
        f"{path.stem}_connected_{args.algorithm}{path.suffix}"
    )

    ctd.process_img(img_load_path, img_save_path, args.algorithm, list(args.line_color))

    logger.info("Done.")
