# Examples

## Example 1 — DOI only

**User:** Visualize the pipeline in DOI `10.18653/v1/N19-1423`

**Agent actions:**

1. `python scripts/fetch_paper.py --doi "10.18653/v1/N19-1423" -o /tmp/bert.json`
2. Scan Method section → find "BERT fine-tuning" baseline described in prose
3. Ask: "Found 1 pipeline (BERT classification baseline, §3). Draw it?"
4. User: yes
5. Write `diagrams/bert-finetuning-baseline.html`
6. Report path and offer tweaks

## Example 2 — Multiple baselines

**User:** DOI 10.xxxx/yyyy — show me all baselines

**Agent:** Lists 3 candidates (BiLSTM, CNN, Transformer). User picks "both 1 and 3".
Generate two HTML files or one diagram with parallel stacks in Output stage.

## Example 3 — User refines

**User:** Merge steps 2 and 3, use green for output

**Agent:** Edit existing HTML — combine boxes, change `box-blue` → `box-green` on final stage.

## Example 4 — No full text

**Agent:** Script returns `full_text: null`, abstract mentions "three-stage pipeline".

Report limited confidence, show draft from abstract, ask user to paste Method section or provide PDF.

## Example 5 — Save from browser

**User:** Export this diagram as PNG for my slide

**Agent:** Tell user to open the `.html` file and click **Save → PNG** under the diagram. Filename comes from the page `<title>`.

## Example 6 — CLI PNG (batch)

**User:** Export the CPC pipeline as PNG for my slide deck

**Agent actions:**

1. Confirm HTML exists at `diagrams/cpc-unsupervised-baseline.html`
2. Run:
   ```bash
   python scripts/html_to_png.py diagrams/cpc-unsupervised-baseline.html -o diagrams/cpc-unsupervised-baseline.png --scale 2
   ```
3. Deliver both `.html` (editable) and `.png` (shareable) paths

## Example 7 — Edit SVG

**User:** Save as SVG and rename "Transformer Predictor" to "1-layer Transformer"

**Agent actions:**

1. Copy `templates/pipeline-diagram.template.svg` → `diagrams/cpc-baseline.svg`
2. Fill labels from pipeline schema
3. Edit `<text class="box-label">1-layer Transformer</text>`
4. Tell user they can open in Inkscape/Figma for further tweaks

See [references/svg-editing.md](references/svg-editing.md) and [references/png-export.md](references/png-export.md).

## Sample extracted structure (CPC-style)

From an unsupervised speech baseline paper:

```yaml
title: "CPC — Unsupervised Baseline"
input:
  label: "Unlabeled Audio"
  sub: "Libri-light subsets"
stages:
  - name: Encoding
    color_theme: pink
    layout: horizontal
    steps:
      - { label: "CNN Encoder", sub: "5 layers · 256-d" }
      - { label: "LSTM", sub: "phonetic embedding" }
  - name: Learning
    color_theme: blue
    layout: vertical_stack
    steps:
      - { label: "InfoNCE Loss", sub: "contrastive" }
      - { label: "ABX Evaluation", sub: "phonetic disc." }
continues: true
```

Maps directly to the HTML in `diagrams/cpc-unsupervised-baseline.html`.
