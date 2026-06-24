# SVG Editing Guide

Use SVG when users need **vector editing** in Inkscape, Figma, Illustrator, or VS Code — or when exporting lossless figures for papers.

## When to use SVG vs HTML

| Format | Best for |
|--------|----------|
| **HTML** | Quick browser preview, CSS layout, agent-generated drafts |
| **SVG** | Manual label tweaks, slide decks, LaTeX `\includesvg`, print at any scale |

Default workflow: generate **HTML first**, then offer **SVG** if the user wants to edit or export for publication.

## Create SVG

1. Copy [templates/pipeline-diagram.template.svg](../templates/pipeline-diagram.template.svg)
2. Replace `<!-- PLACEHOLDER -->` comments with labels from the paper
3. Save as `diagrams/<slug>-pipeline.svg`
4. Keep the same color fills as HTML (see style-guide palette)

## Edit SVG (agent or user)

Common edits — modify XML directly or in a vector editor:

| Change | SVG approach |
|--------|----------------|
| Rename a step | Edit `<text class="box-label">…</text>` |
| Add subtitle | Edit `<text class="box-sub">…</text>` |
| Change stage color | Update `fill="#f5c6cb"` on `<rect>` (pink/yellow/blue/green/orange) |
| Move a box | Adjust `x`, `y`, `width`, `height` on the box `<rect>` and its `<text>` nodes |
| Add a step | Duplicate a box `<rect>` + two `<text>` nodes; add `<line marker-end="url(#arrowhead)">` |
| Dashed stage | `stroke-dasharray="8 5"` on stage `<rect>` |

**Arrow marker** is defined once in `<defs>` — reuse `marker-end="url(#arrowhead)"` on `<line>` elements.

## Color reference (same as HTML)

| Role | Fill |
|------|------|
| Pink | `#f5c6cb` |
| Yellow | `#fff3cd` |
| Blue | `#cce5ff` |
| Green | `#c3e6cb` |
| Orange | `#ffddc1` |
| Stage border | `#c8c8c8` dashed |
| Arrows / text | `#333` / `#222` |

## Export SVG → PNG

**Option A — Inkscape (CLI):**

```bash
inkscape diagrams/my-pipeline.svg --export-type=png --export-filename=diagrams/my-pipeline.png -d 192
```

**Option B — rsvg-convert:**

```bash
rsvg-convert -w 2200 diagrams/my-pipeline.svg -o diagrams/my-pipeline.png
```

**Option C — Browser:** open SVG in Chrome → right-click → Save as PNG (quick, lower control).

## Sync HTML ↔ SVG

If user edits one format, offer to sync the other:

- **HTML → SVG:** Regenerate SVG from the structured pipeline schema (Step 4 in SKILL.md)
- **SVG → HTML:** Read text labels and box positions; rebuild HTML only if layout is still horizontal-chain compatible

Do not auto-sync without asking — manual SVG edits may break 1:1 layout mapping.

## Quality check

- [ ] All text readable at 100% zoom
- [ ] Stage titles sit above dashed borders (white rect behind text)
- [ ] Arrowheads point in flow direction
- [ ] `viewBox` trimmed or canvas sized to content (no huge empty margins)
