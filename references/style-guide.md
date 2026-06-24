# Flowchart Draw — Visual Style Guide

Match the reference images in `ref_pictures/` and the worked example at
`../../diagrams/cpc-unsupervised-baseline.html` (if present in workspace).

## Design principles

1. **Left-to-right** main flow; use **vertical stacks** inside a stage for parallel or alternative sub-steps
2. **Dashed stage boxes** segment the pipeline into named phases (Preprocessing, Encoding, Learning, Output)
3. **Color encodes role**, not decoration — keep colors consistent within a stage
4. **Black arrows** show execution order; one direction only unless paper explicitly has feedback loops
5. **Minimal text** — box label + optional `<small>` subtitle for dimensions/hyperparams

## Color palette

| Class | Background | Use for |
|-------|------------|---------|
| `.box-pink` | `#f5c6cb` | Input transformation, tokenization, early encoding |
| `.box-yellow` | `#fff3cd` | Intermediate modules, taggers, predictors, stacked alternatives |
| `.box-blue` | `#cce5ff` | Loss, training objectives, evaluation, downstream heads |
| `.box-green` | `#c3e6cb` | Output tasks, predictions, final labels |
| `.box-orange` | `#ffddc1` | Classical preprocessing (tokenize, POS, stopwords) |

Stage dashed border default: `#c8c8c8`. Optional themed borders:
- Preprocessing stage: `#e8a87c` (orange tint)
- Modeling stage: `#6baed6` (blue tint)
- Output stage: `#74c476` (green tint)

## HTML structure

```html
<div class="diagram">
  <!-- Optional input -->
  <div class="input-block">...</div>
  <div class="arrow"></div>

  <!-- Stage: dashed container -->
  <div class="stage">
    <div class="stage-title">Stage Name</div>
    <div class="stage-inner">   <!-- horizontal -->
      <div class="box box-pink">Step A<small>detail</small></div>
      <div class="arrow"></div>
      <div class="box box-pink">Step B</div>
    </div>
  </div>

  <div class="arrow"></div>

  <!-- Stage with vertical stack -->
  <div class="stage">
    <div class="stage-title">Learning</div>
    <div class="stack">
      <div class="box box-blue">Task 1</div>
      <div class="box box-blue">Task 2</div>
      <div class="box box-blue" style="font-size:20px; padding:6px 20px;">…</div>
    </div>
  </div>

  <div class="arrow"></div>
  <div class="ellipsis">…</div>   <!-- if pipeline continues -->
</div>
```

## CSS essentials (copy into every diagram)

```css
.stage {
  border: 2px dashed #c8c8c8;
  border-radius: 18px;
  padding: 28px 24px 22px;
  position: relative;
}
.stage-title {
  position: absolute;
  top: -13px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  padding: 0 12px;
  font-size: 17px;
  font-weight: 700;
}
.box {
  border-radius: 14px;
  border: 1.5px solid rgba(0,0,0,0.12);
  padding: 14px 20px;
  font-size: 15px;
  font-weight: 600;
}
.arrow {
  width: 36px;
  height: 2px;
  background: #333;
  position: relative;
}
.arrow::after {
  content: "";
  position: absolute;
  right: -1px;
  top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent;
  border-left: 8px solid #333;
}
```

## Layout rules

| Pattern | When to use |
|---------|-------------|
| Single horizontal chain | Linear pipeline (tokenize → encode → classify) |
| Vertical stack in one stage | Multiple downstream tasks or baseline variants |
| Input icon block | Clear modality: text, audio waveform, documents |
| Trailing `…` | Paper describes further stages not drawn |
| Multiple `.stage` in sequence | Paper uses explicit phase names |

## Do not

- Use dark backgrounds or gradient fills
- Add icons inside every box (keep boxes text-only unless input block)
- Draw bidirectional arrows unless paper describes iterative refinement
- Copy figure text verbatim if it exceeds ~6 words per box — abbreviate sensibly

## Quality check

Before delivering, verify:

- [ ] Every stage has a visible dashed border and title
- [ ] Arrow count matches logical flow (no orphan boxes)
- [ ] Colors are consistent within each stage
- [ ] Labels match paper terminology (model names, loss names)
- [ ] Caption at bottom: `Author Year · Pipeline name · Source section`
