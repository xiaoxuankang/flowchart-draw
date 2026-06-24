# HTML → PNG Export

Convert self-contained pipeline HTML diagrams to PNG for slides, papers, and README embeds.

## Script

```bash
python scripts/html_to_png.py diagrams/my-pipeline.html
python scripts/html_to_png.py diagrams/my-pipeline.html -o figures/my-pipeline.png --scale 2
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-o`, `--output` | `<input>.png` | Output file path |
| `--selector` | `.diagram` | CSS selector for crop region |
| `--scale` | `2` | Device scale (2 = retina, 3 = print) |
| `--full-page` | off | Capture entire page instead of diagram |
| `--padding` | `24` | Padding around diagram clip (px) |

### Setup (one-time)

```bash
pip install playwright
playwright install chromium
```

Or install all skill dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Agent workflow

After saving `diagrams/<slug>-pipeline.html`:

1. Run `html_to_png.py` with matching output path
2. Tell user both paths: `.html` (editable) and `.png` (shareable)
3. If playwright missing, suggest browser screenshot or install steps above

## Multi-row diagrams

For benchmark overviews with class `.rows` instead of `.diagram`:

```bash
python scripts/html_to_png.py diagrams/libri-light-benchmark.html --selector ".rows" --full-page
```

Or use `--full-page` when the layout spans multiple rows.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Blank PNG | Ensure HTML uses `file://` path; run from machine with display/Chromium |
| Cropped text | Increase `--padding` or use `--full-page` |
| Blurry PNG | Raise `--scale` to 2 or 3 |
| `playwright not found` | `pip install playwright && playwright install chromium` |
