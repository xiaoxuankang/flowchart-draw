# Save Button (PNG / PDF)

Every generated HTML diagram must include a **Save** bar below the preview so users can export without running scripts.

## Required structure

```html
<div id="export-root" class="export-root">
  <!-- title, diagram (.diagram or .rows), caption -->
</div>

<div class="save-bar" aria-label="Export diagram">
  <span class="save-label">Save</span>
  <button type="button" id="btn-save-png">PNG</button>
  <button type="button" id="btn-save-pdf">PDF</button>
  <span class="save-status" id="save-status"></span>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script>/* inline copy from templates/diagram-save.js */</script>
```

- **`#export-root`** — everything to capture (title + diagram + caption). Do **not** include the save bar inside it.
- **Filename** — derived from `<title>` (slugified).

## CSS (add to `<style>`)

```css
.save-bar {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}
.save-label {
  font-size: 14px;
  font-weight: 700;
  color: #444;
}
.save-bar button {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1.5px solid #333;
  background: #fff;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  color: #222;
  cursor: pointer;
}
.save-bar button:hover { background: #f5f5f5; }
.save-bar button:disabled { opacity: 0.5; cursor: wait; }
.save-status {
  font-size: 12px;
  color: #666;
  min-height: 1em;
}
```

## Multi-row layouts

For benchmark-style pages with `.rows`, wrap `<h1>`, `.rows`, and `.caption-wrap` inside `#export-root`.

## Agent checklist

- [ ] `#export-root` wraps all visible diagram content
- [ ] Save bar placed **below** caption, above `</body>`
- [ ] CDN scripts + `diagram-save.js` logic included
- [ ] `<title>` set to a meaningful export filename

## Offline / CLI fallback

If CDN is blocked, use `scripts/html_to_png.py` (Playwright) for PNG only. PDF requires the in-browser Save button or print-to-PDF.
