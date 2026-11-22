# Visual Template Finder

Locate a known grayscale symbol in a larger image when its brightness and contrast have changed. The matcher scans every possible position and scores each patch using zero-mean normalised cross-correlation.

```sh
python template_finder.py
python -m unittest -v
```

The demo embeds a contrast-adjusted 4×4 symbol in a seeded 32×48 frame. It recovers row **17**, column **29**, with a score of **1.000**. Tests also exercise flat patches, reversed contrast, and malformed input.

To search your own grayscale image, supply two plain-text P2 PGM files. Coordinates start at zero.

```sh
python template_finder.py --image frame.pgm --template symbol.pgm --minimum-score 0.95
```

The score compares intensity patterns after centering and rescaling. It ranges from −1 to 1. A cutoff lets the caller decline weak matches. The exhaustive search is suitable for small images. Changes in scale, rotation, occlusion, or repeated symbols would need a more capable detector.

This standalone AI-assisted portfolio project uses synthetic imagery and the Python 3.10+ standard library.
