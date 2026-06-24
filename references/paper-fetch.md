# Paper Fetch — DOI Resolution

Primary tool: `scripts/fetch_paper.py`

## Resolution chain

```
DOI normalize
  → OpenAlex (metadata + abstract + open access URL)
  → Semantic Scholar (full text snippet, PDF link, citation)
  → arXiv (if arXiv ID found in metadata)
  → PDF text extraction (if PDF URL available)
  → Jina Reader fallback on PDF/HTML URL
```

## Manual fallbacks

If the script returns `"full_text": null`:

### 1. arXiv by DOI

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=externalIds,openAccessPdf" 
```

If `arxivId` present:

```bash
curl -s "https://arxiv.org/e-print/<arxivId>" -o paper.pdf
# Or read TeX source for cleaner text
```

### 2. Jina Reader (HTML/PDF URL)

```bash
curl -s "https://r.jina.ai/https://doi.org/<doi>"
```

Or on a direct PDF URL from OpenAlex `open_access.oa_url`.

### 3. Semantic Scholar full text

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=title,abstract,tldr,openAccessPdf,citationStyles"
```

### 4. User provides PDF

Ask user to drop PDF in workspace; extract with:

```bash
python -c "import fitz; d=fitz.open('paper.pdf'); print(''.join(p.get_text() for p in d))"
```

(requires `pymupdf`: `pip install pymupdf`)

## DOI normalization

Accept and strip:

- `10.1234/example`
- `https://doi.org/10.1234/example`
- `http://dx.doi.org/10.1234/example`
- `doi:10.1234/example`

## Output JSON schema

```json
{
  "doi": "10.xxxx/yyyy",
  "title": "...",
  "authors": ["..."],
  "year": 2024,
  "venue": "...",
  "abstract": "...",
  "full_text": "... or null",
  "pdf_url": "... or null",
  "arxiv_id": "... or null",
  "source": "openalex+arxiv",
  "has_existing_figures": true,
  "sections": [{"heading": "Method", "text": "..."}],
  "fetch_warnings": []
}
```

## Figure detection

`has_existing_figures` is true if full text contains patterns:

- `Figure 1`, `Fig. 1`, `FIGURE 1`
- `graphical abstract`
- `\begin{figure}` (LaTeX)

Use this as a soft signal only — still inspect each candidate section locally.

## Rate limits

- OpenAlex: polite pool, no key required; add `mailto=` query param
- Semantic Scholar: ~100 req/5min unauthenticated
- Sleep 1s between retries on 429

## Errors

| Error | Action |
|-------|--------|
| DOI not found | Ask user for title + arXiv link |
| Paywall, no OA PDF | Use abstract + method snippets from S2; ask user for PDF |
| PDF extract failed | Jina reader or user upload |
| Non-English paper | Proceed if user wants; note language in caption |
