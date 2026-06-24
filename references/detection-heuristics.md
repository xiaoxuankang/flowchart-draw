# Pipeline Detection Heuristics

Use these rules after fetching paper text to find sections that **benefit from a flowchart**.

## Strong signals (likely needs diagram)

Score each section; **≥3 strong signals** → propose to user.

1. **Sequential process language**: "first … then … next … finally", numbered steps (1)(2)(3), "followed by"
2. **Multi-component architecture**: encoder-decoder, pipeline, stack, cascade, module names chained together
3. **Baseline / method comparison**: "our approach consists of", "the baseline uses", "we compare against"
4. **Data flow verbs**: input → transform → encode → predict → output, "fed into", "passed to", "concatenated with"
5. **Long paragraph (≥4 sentences)** describing steps without a nearby figure reference
6. **Section headers**: Method, Architecture, Model, Pipeline, Baselines, System Overview, Framework, Approach

## Weak signals (supporting)

- Lists of model components (BERT, CRF, softmax)
- Training vs inference described separately (draw two paths or two diagrams)
- Ablation describing removed stages
- "Figure X illustrates" absent within ±2 paragraphs of the description

## Skip (do not propose)

- Section already references **Figure N** / **Algorithm N** showing the same flow
- Pure math notation with no procedural steps
- Related work summarizing others' methods (unless user asks)
- Hyperparameter tables only
- Evaluation protocol (train/dev/test split) unless it is the main contribution

## Section priority

Search in order:

1. Abstract (quick scan — rarely draw from abstract alone)
2. Method / Approach / Architecture
3. Baselines / Experimental Setup
4. Appendix (often has full pipeline detail omitted from main text)

## Candidate report template

```markdown
### Candidate 1: [Short name]
- **Location**: §3.2 Baselines, paragraphs 2–4
- **Confidence**: High / Medium
- **Existing figure?**: No (Figure 2 shows dataset stats only)
- **Extracted flow**:
  1. Input: raw clinical notes
  2. Preprocessing: tokenization, lowercasing
  3. Encoder: BioBERT
  4. Head: linear + CRF
  5. Output: entity spans
- **Suggested stages**: Preprocessing | Encoding | Prediction
```

## Multi-pipeline papers

Common patterns:

| Paper type | Action |
|------------|--------|
| Main model + baselines | One candidate per baseline; ask user which to draw |
| Train vs test | Single diagram with two colored paths (see ref `1_87x5Ef-nxSx2Gsp17zxQlg.png`) |
| Classical vs DL | Side-by-side or separate HTML files |
| Ensemble | Vertical stack of models → fusion box |

## Confidence levels

- **High**: Named stages + order + no figure
- **Medium**: Implicit order, some ambiguity in grouping
- **Low**: Mentioned in passing — list but don't auto-recommend

Only auto-recommend High and Medium candidates.
