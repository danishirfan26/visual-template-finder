from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from template_finder import find_template, read_plain_pgm


class TemplateFinderTests(unittest.TestCase):
    def test_finds_brightness_shifted_template(self):
        pattern = [[1, 4], [2, 3]]
        image = [[0, 0, 0], [0, 12, 18], [0, 14, 16]]
        result = find_template(image, pattern)
        self.assertEqual((result.row, result.column), (1, 1))
        self.assertAlmostEqual(result.score, 1)

    def test_flat_image_and_low_scores_produce_no_detection(self):
        self.assertIsNone(find_template([[3, 3], [3, 3]], [[1, 2], [3, 4]]))
        self.assertIsNone(find_template([[4, 3], [2, 1]], [[1, 2], [3, 4]]))

    def test_invalid_geometry_and_constant_template(self):
        with self.assertRaises(ValueError):
            find_template([[1], [1, 2]], [[1]])
        with self.assertRaises(ValueError):
            find_template([[1, 2]], [[1, 1]])

    def test_reads_pgm_comments_and_rejects_invalid_pixels(self):
        with TemporaryDirectory() as directory:
            image_path = Path(directory) / "image.pgm"
            image_path.write_text("P2\n# two rows\n2 2\n9\n1 2 3 4\n", encoding="ascii")
            self.assertEqual(read_plain_pgm(image_path), [[1, 2], [3, 4]])
            image_path.write_text("P2\n2 2\n9\n1 2 3 10\n", encoding="ascii")
            with self.assertRaises(ValueError):
                read_plain_pgm(image_path)
