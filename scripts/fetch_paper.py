#!/usr/bin/env python3
"""
Fetch paper metadata and text by DOI for the flowchart-draw skill.

Usage:
  python fetch_paper.py --doi "10.18653/v1/N19-1423"
  python fetch_paper.py --doi "10.18653/v1/N19-1423" --output paper.json

Dependencies: stdlib only. Optional: pymupdf for better PDF text extraction.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

USER_AGENT = "flowchart-draw/1.0 (mailto:user@example.com)"
REQUEST_TIMEOUT = 30


def normalize_doi(raw: str) -> str:
    doi = raw.strip()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
        "DOI:",
    ):
        if doi.lower().startswith(prefix.lower()):
            doi = doi[len(prefix) :]
            break
    return doi.strip().rstrip(".")


def http_get(url: str, headers: dict[str, str] | None = None, retries: int = 3) -> tuple[int, str]:
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace") if e.fp else ""
            return e.code, body
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    if last_err:
        raise last_err
    return 0, ""


def fetch_openalex(doi: str) -> dict[str, Any] | None:
    encoded = urllib.parse.quote(f"https://doi.org/{doi}", safe="")
    url = (
        f"https://api.openalex.org/works/{encoded}"
        f"?mailto=user@example.com"
    )
    try:
        status, body = http_get(url)
    except Exception:
        return None
    if status != 200:
        return None
    data = json.loads(body)
    authors = []
    for auth in data.get("authorships") or []:
        name = (auth.get("author") or {}).get("display_name")
        if name:
            authors.append(name)

    pdf_url = None
    oa = data.get("open_access") or {}
    if oa.get("oa_url"):
        pdf_url = oa["oa_url"]
    for loc in data.get("locations") or []:
        if loc.get("pdf_url") and not pdf_url:
            pdf_url = loc["pdf_url"]

    arxiv_id = None
    for alt in data.get("ids") or {}:
        if "arxiv" in alt.lower():
            arxiv_id = data["ids"][alt].split("/")[-1]
            break
    # OpenAlex sometimes stores arxiv in primary_location
    pl = data.get("primary_location") or {}
    src = pl.get("source") or {}
    if src.get("display_name") == "arXiv" and data.get("ids", {}).get("doi"):
        pass
    if data.get("ids", {}).get("arxiv"):
        arxiv_id = data["ids"]["arxiv"].replace("https://arxiv.org/abs/", "")

    return {
        "title": data.get("display_name") or data.get("title"),
        "authors": authors,
        "year": data.get("publication_year"),
        "venue": ((data.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "abstract": reconstruct_abstract(data.get("abstract_inverted_index")),
        "pdf_url": pdf_url,
        "arxiv_id": arxiv_id,
        "openalex_id": data.get("id"),
    }


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not inverted_index:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words.append((pos, word))
    words.sort(key=lambda x: x[0])
    return " ".join(w for _, w in words)


def fetch_semantic_scholar(doi: str) -> dict[str, Any] | None:
    fields = "title,authors,year,venue,abstract,externalIds,openAccessPdf,tldr"
    url = (
        "https://api.semanticscholar.org/graph/v1/paper/"
        f"DOI:{urllib.parse.quote(doi, safe='')}?fields={fields}"
    )
    try:
        status, body = http_get(url)
    except Exception:
        return None
    if status != 200:
        return None
    data = json.loads(body)
    authors = [a.get("name", "") for a in data.get("authors") or [] if a.get("name")]
    pdf_url = None
    oap = data.get("openAccessPdf") or {}
    if oap.get("url"):
        pdf_url = oap["url"]
    ext = data.get("externalIds") or {}
    return {
        "title": data.get("title"),
        "authors": authors,
        "year": data.get("year"),
        "venue": data.get("venue"),
        "abstract": data.get("abstract") or (data.get("tldr") or {}).get("text"),
        "pdf_url": pdf_url,
        "arxiv_id": ext.get("ArXiv"),
    }


def fetch_arxiv_text(arxiv_id: str) -> str | None:
    arxiv_id = arxiv_id.replace("arxiv:", "").strip()
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}"
    status, body = http_get(url, headers={"Accept": "application/atom+xml"})
    if status != 200:
        return None
    summaries = re.findall(r"<summary[^>]*>([\s\S]*?)</summary>", body)
    if len(summaries) >= 2:
        # First summary is feed-level; second is paper abstract in atom
        text = summaries[1]
        text = re.sub(r"\s+", " ", text).strip()
        return text
    return None


def fetch_arxiv_pdf_text(arxiv_id: str) -> str | None:
    """Try pymupdf on arXiv PDF; fall back to Jina reader."""
    arxiv_id = arxiv_id.replace("arxiv:", "").strip()
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    return fetch_pdf_text(pdf_url) or fetch_jina_reader(pdf_url)


def fetch_pdf_text(url: str) -> str | None:
    try:
        import fitz  # pymupdf
    except ImportError:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            pdf_bytes = resp.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        parts = []
        for page in doc:
            parts.append(page.get_text())
        doc.close()
        text = "\n".join(parts).strip()
        return text if len(text) > 200 else None
    except Exception:
        return None


def fetch_jina_reader(url: str) -> str | None:
    jina_url = f"https://r.jina.ai/{url}"
    try:
        status, body = http_get(jina_url, headers={"Accept": "text/plain"})
    except Exception:
        return None
    if status != 200 or len(body) < 200:
        return None
    return body


def detect_existing_figures(text: str) -> bool:
    patterns = [
        r"\bFigure\s+\d+",
        r"\bFig\.\s*\d+",
        r"\bFIGURE\s+\d+",
        r"\\begin\{figure\}",
        r"graphical abstract",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def split_sections(text: str) -> list[dict[str, str]]:
    """Heuristic section split on numbered or common NLP paper headings."""
    heading_pattern = re.compile(
        r"(?m)^(?:\d+\.?\s+)?("
        r"Abstract|Introduction|Related Work|Background|Method(?:ology)?|"
        r"Approach|Model|Architecture|Experiments?|Results?|Discussion|"
        r"Conclusion|Baselines?|Implementation|Appendix"
        r")\s*$",
        re.IGNORECASE,
    )
    sections: list[dict[str, str]] = []
    matches = list(heading_pattern.finditer(text))
    if not matches:
        return [{"heading": "Full text", "text": text[:50000]}]
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append({"heading": m.group(1).strip(), "text": text[start:end].strip()})
    return sections


def merge_metadata(*sources: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for src in sources:
        if not src:
            continue
        for k, v in src.items():
            if v is not None and (k not in merged or merged[k] in (None, "", [])):
                merged[k] = v
    return merged


def fetch_paper(doi: str) -> dict[str, Any]:
    warnings: list[str] = []
    sources_used: list[str] = []

    oa = fetch_openalex(doi)
    if oa:
        sources_used.append("openalex")
    else:
        warnings.append("OpenAlex lookup failed")
    time.sleep(0.3)

    s2 = fetch_semantic_scholar(doi)
    if s2:
        sources_used.append("semantic_scholar")
    else:
        warnings.append("Semantic Scholar lookup failed")
    meta = merge_metadata(oa, s2)

    if not meta.get("title"):
        return {
            "doi": doi,
            "error": "DOI not found in OpenAlex or Semantic Scholar",
            "fetch_warnings": warnings,
        }

    full_text: str | None = None
    arxiv_id = meta.get("arxiv_id")
    pdf_url = meta.get("pdf_url")

    if arxiv_id:
        sources_used.append("arxiv")
        full_text = fetch_arxiv_pdf_text(str(arxiv_id))
        if not full_text:
            abs_text = fetch_arxiv_text(str(arxiv_id))
            if abs_text:
                full_text = abs_text
                warnings.append("Only arXiv abstract retrieved; full PDF text unavailable")

    if not full_text and pdf_url:
        full_text = fetch_pdf_text(pdf_url)
        if full_text:
            sources_used.append("pdf+pymupdf")
        else:
            full_text = fetch_jina_reader(pdf_url)
            if full_text:
                sources_used.append("jina_reader")

    if not full_text:
        warnings.append(
            "No full text retrieved. Install pymupdf (pip install pymupdf) "
            "or provide PDF manually. Using abstract only."
        )
        full_text = meta.get("abstract")

    text_for_figures = full_text or meta.get("abstract") or ""
    sections = split_sections(text_for_figures) if text_for_figures else []

    return {
        "doi": doi,
        "title": meta.get("title"),
        "authors": meta.get("authors") or [],
        "year": meta.get("year"),
        "venue": meta.get("venue"),
        "abstract": meta.get("abstract"),
        "full_text": full_text,
        "pdf_url": pdf_url,
        "arxiv_id": arxiv_id,
        "source": "+".join(dict.fromkeys(sources_used)),
        "has_existing_figures": detect_existing_figures(text_for_figures),
        "sections": sections,
        "fetch_warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch paper by DOI for flowchart-draw skill")
    parser.add_argument("--doi", required=True, help="DOI or doi.org URL")
    parser.add_argument("--output", "-o", help="Write JSON to file (default: stdout)")
    args = parser.parse_args()

    doi = normalize_doi(args.doi)
    if not doi:
        print("Error: empty DOI", file=sys.stderr)
        return 1

    result = fetch_paper(doi)
    payload = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(payload)

    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
