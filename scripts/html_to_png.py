#!/usr/bin/env python3
"""
Render a pipeline HTML diagram to PNG.

Usage:
  python scripts/html_to_png.py diagrams/my-pipeline.html
  python scripts/html_to_png.py diagrams/my-pipeline.html -o output.png --scale 2

Requires: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def render_png(
    html_path: Path,
    output_path: Path,
    selector: str = ".diagram",
    scale: float = 2.0,
    full_page: bool = False,
    padding: int = 24,
) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "playwright is required. Install with:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        ) from exc

    html_path = html_path.resolve()
    if not html_path.exists():
        raise SystemExit(f"HTML file not found: {html_path}")

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    file_url = html_path.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1400, "height": 900},
            device_scale_factor=scale,
        )
        page.goto(file_url, wait_until="networkidle")

        if full_page:
            page.screenshot(path=str(output_path), full_page=True)
        else:
            element = page.query_selector(selector)
            if element is None:
                print(
                    f"Warning: selector '{selector}' not found; capturing full page.",
                    file=sys.stderr,
                )
                page.screenshot(path=str(output_path), full_page=True)
            else:
                box = element.bounding_box()
                if box:
                    page.screenshot(
                        path=str(output_path),
                        clip={
                            "x": max(0, box["x"] - padding),
                            "y": max(0, box["y"] - padding),
                            "width": box["width"] + padding * 2,
                            "height": box["height"] + padding * 2,
                        },
                    )
                else:
                    element.screenshot(path=str(output_path))

        browser.close()

    print(f"Wrote {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert pipeline HTML diagram to PNG")
    parser.add_argument("html", type=Path, help="Path to .html diagram file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .png path (default: same name as HTML)",
    )
    parser.add_argument(
        "--selector",
        default=".diagram",
        help="CSS selector for the diagram region (default: .diagram)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="Device scale factor for retina-quality PNG (default: 2)",
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="Capture entire page instead of diagram selector",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=24,
        help="Padding around diagram clip in pixels (default: 24)",
    )
    args = parser.parse_args()

    output = args.output or args.html.with_suffix(".png")
    render_png(
        html_path=args.html,
        output_path=output,
        selector=args.selector,
        scale=args.scale,
        full_page=args.full_page,
        padding=args.padding,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
