---
name: flowchart-draw
description: >
  Reads NLP/ML papers by DOI, detects methodology or baseline sections that
  describe pipelines in prose without flowcharts, and generates colored HTML
  pipeline diagrams (dashed stage boxes, colored step boxes, black arrows).
  Use when user gives a paper DOI, asks to visualize a baseline/pipeline/architecture,
  wants a flowchart from a paper, or mentions NLP pipeline diagrams.
---

# Flowchart Draw

Turn prose pipeline descriptions in papers into readable flowcharts.

## Quick start

```
User: Draw the pipeline for DOI 10.18653/v1/N19-1423

1. python scripts/fetch_paper.py --doi "10.18653/v1/N19-1423" --output /tmp/paper.json
2. Read paper JSON + scan for pipeline candidates (see detection heuristics)
3. Present candidates → ask user which to draw
4. Generate HTML from template → save to diagrams/<short-title>-pipeline.html
5. Open in browser for review
```

## Workflow checklist

Copy and track progress:

```
Flowchart Draw Progress:
- [ ] Step 1: Resolve DOI → fetch metadata + full text
- [ ] Step 2: Scan paper for pipeline/baseline descriptions lacking figures
- [ ] Step 3: Present candidates and ask user to confirm
- [ ] Step 4: Extract structured pipeline (stages, steps, order, I/O)
- [ ] Step 5: Generate HTML diagram (style guide)
- [ ] Step 6: Save file and show preview path
```

## Step 1 — Fetch paper

Run from this skill directory:

```bash
python scripts/fetch_paper.py --doi "<DOI>" --output paper.json
```

- Accept bare DOI (`10.1234/abc`) or full URL (`https://doi.org/10.1234/abc`).
- If `--output` omitted, prints JSON to stdout.
- On failure, follow [references/paper-fetch.md](references/paper-fetch.md) fallbacks
  (arXiv ID, Semantic Scholar, Jina reader on PDF URL).

Read the returned JSON fields: `title`, `authors`, `abstract`, `sections`, `full_text`,
`has_existing_figures`, `pdf_url`, `source`.

## Step 2 — Detect pipeline candidates

Apply heuristics in [references/detection-heuristics.md](references/detection-heuristics.md).

For each candidate, report to the user:

| Field | Example |
|-------|---------|
| **Name** | "BERT fine-tuning baseline" |
| **Section** | §3.2 Baselines |
| **Why** | 5 sequential steps, no Figure/Algorithm nearby |
| **Steps (draft)** | Tokenize → BERT encoder → [CLS] → linear → softmax |

**Skip** if the paper already has a figure covering the same content (check
`has_existing_figures` and nearby "Figure N" references in that section).

## Step 3 — Ask before drawing

**Always confirm** with the user before generating. Use AskQuestion or a numbered list:

> I found **2 pipeline descriptions** without diagrams:
> 1. Main model architecture (§3.1)
> 2. Baseline comparison — BiLSTM-CRF (§4.2)
>
> Which should I draw? (1 / 2 / both / none)

If the user only gave a DOI with no other instruction, still present candidates first.

## Step 4 — Extract structure

Build an internal schema before coding HTML:

```yaml
title: "Paper Short Title — Pipeline Name"
input:
  label: "Raw Text"
  sub: "optional detail"
stages:
  - name: "Preprocessing"
    color_theme: pink    # pink | yellow | blue | green | orange
    layout: horizontal   # horizontal | vertical_stack
    steps:
      - label: "Tokenization"
        sub: "WordPiece, 30k vocab"
      - label: "NER"
        sub: ""
  - name: "Learning"
    color_theme: blue
    layout: vertical_stack
    steps:
      - label: "BERT Encoder"
      - label: "Classification Head"
output:
  label: "Predictions"
  sub: "softmax over labels"
continues: true   # show trailing "…" if pipeline extends
```

Match stage groupings to the paper's own terminology (Preprocessing / Encoding / Learning / Output).

## Step 5 — Generate diagram

Follow [references/style-guide.md](references/style-guide.md) exactly:

- **Dashed rounded rectangles** (`.stage`) group related steps; title floats above border
- **Colored rounded boxes** (`.box-pink`, `.box-yellow`, `.box-blue`, `.box-green`, `.box-orange`)
- **Black horizontal arrows** (`.arrow`) between stages and sequential steps
- **Input block** on the far left (icon + label) when paper has clear input modality
- White background, no dark theme

Start from [templates/pipeline-diagram.template.html](templates/pipeline-diagram.template.html).
See [examples/libri-light-cpc-pipeline.html](examples/libri-light-cpc-pipeline.html) for a worked output.

Save to `diagrams/<slug>-pipeline.html` (workspace) or user-specified path.
Use a filesystem-safe slug from paper title + pipeline name.

## Step 6 — Deliver

Tell the user:
- Saved file path
- How to open (`file://` or `Open with Live Server`)
- One-sentence summary of what the diagram shows
- Offer to adjust colors, add/remove steps, or draw another candidate

## Common adjustments

| Request | Action |
|---------|--------|
| Add baseline comparison | Duplicate stage row or second diagram file |
| Match paper colors | Swap `box-*` classes per stage theme |
| Simpler diagram | Collapse substeps into one box with `<small>` details |
| Export PNG | Open HTML → browser print/screenshot, or ask user preference |

## Additional references

- Visual spec: [references/style-guide.md](references/style-guide.md)
- Detection rules: [references/detection-heuristics.md](references/detection-heuristics.md)
- DOI fallbacks: [references/paper-fetch.md](references/paper-fetch.md)
- Worked example: [EXAMPLES.md](EXAMPLES.md)
