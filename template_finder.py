"""Find a small grayscale motif in a larger image."""

import argparse
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from random import Random


@dataclass(frozen=True)
class Match:
    row: int
    column: int
    score: float


def shape(image):
    if not image or not image[0] or any(len(row) != len(image[0]) for row in image):
        raise ValueError("Expected a nonempty rectangular image")
    return len(image), len(image[0])


def centered(values):
    mean = sum(values) / len(values)
    offsets = [value - mean for value in values]
    return offsets, sqrt(sum(value * value for value in offsets))


def find_template(image, template, minimum_score=0.90):
    """Return the best match above the cutoff, resolving ties in reading order."""
    height, width = shape(image)
    tile_height, tile_width = shape(template)
    if tile_height > height or tile_width > width:
        raise ValueError("Template must fit inside the image")
    if not -1 <= minimum_score <= 1:
        raise ValueError("Score must be between -1 and 1")
    reference, reference_norm = centered([pixel for row in template for pixel in row])
    if reference_norm == 0:
        raise ValueError("Template must have contrast")

    best = None
    for row in range(height - tile_height + 1):
        for column in range(width - tile_width + 1):
            pixels = [pixel for line in image[row:row + tile_height]
                      for pixel in line[column:column + tile_width]]
            offsets, norm = centered(pixels)
            if norm == 0:
                continue
            dot = sum(a * b for a, b in zip(reference, offsets))
            score = max(-1.0, min(1.0, dot / (reference_norm * norm)))
            if score >= minimum_score and (best is None or score > best.score + 1e-12):
                best = Match(row, column, score)
    return best


def read_plain_pgm(path):
    """Read a text P2 PGM image, including comments and arbitrary whitespace."""
    tokens = [token for line in path.read_text(encoding="ascii").splitlines()
              for token in line.split("#", 1)[0].split()]
    if len(tokens) < 4 or tokens[0] != "P2":
        raise ValueError("Expected a text P2 PGM image")
    width, height, maximum = map(int, tokens[1:4])
    if width <= 0 or height <= 0 or not 1 <= maximum <= 65535:
        raise ValueError("PGM header has invalid dimensions or maximum intensity")
    pixels = list(map(int, tokens[4:]))
    if len(pixels) != width * height or any(not 0 <= pixel <= maximum for pixel in pixels):
        raise ValueError("PGM pixel values do not match the header")
    return [pixels[start:start + width] for start in range(0, len(pixels), width)]


def demo_image():
    rng = Random(26)
    image = [[rng.randint(35, 100) for _ in range(48)] for _ in range(32)]
    template = [[10, 10, 90, 10], [10, 90, 90, 10],
                [90, 90, 90, 90], [10, 10, 90, 10]]
    expected = (17, 29)
    for y, row in enumerate(template):
        for x, pixel in enumerate(row):
            image[expected[0] + y][expected[1] + x] = 25 + 2 * pixel
    return image, template, expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--minimum-score", type=float, default=0.90)
    args = parser.parse_args()
    if (args.image is None) != (args.template is None):
        parser.error("Provide both --image and --template for a custom image")
    try:
        if args.image:
            image, template = read_plain_pgm(args.image), read_plain_pgm(args.template)
        else:
            image, template, expected = demo_image()
            print(f"Expected row, column: {expected}")
        match = find_template(image, template, args.minimum_score)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    if match is None:
        print("No match reached the requested score")
    else:
        print(f"Found: ({match.row}, {match.column}) | score {match.score:.3f}")


if __name__ == "__main__":
    main()
