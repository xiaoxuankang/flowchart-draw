/**
 * Client-side PNG / PDF export for flowchart-draw HTML diagrams.
 * Include after html2canvas + jsPDF CDN scripts. Requires #export-root in the page.
 */
(function () {
  "use strict";

  function slugify(text) {
    return (text || "pipeline-diagram")
      .replace(/[^\w\s\-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .toLowerCase() || "pipeline-diagram";
  }

  function setStatus(msg) {
    var el = document.getElementById("save-status");
    if (el) el.textContent = msg || "";
  }

  function captureRoot() {
    var root = document.getElementById("export-root");
    if (!root) throw new Error("Missing #export-root wrapper");
    return root;
  }

  function renderCanvas(root) {
    if (typeof html2canvas !== "function") {
      throw new Error("html2canvas not loaded");
    }
    return html2canvas(root, {
      scale: 2,
      backgroundColor: "#ffffff",
      useCORS: true,
      logging: false,
      scrollX: 0,
      scrollY: -window.scrollY,
      windowWidth: root.scrollWidth,
      windowHeight: root.scrollHeight,
    });
  }

  function downloadBlob(href, filename) {
    var link = document.createElement("a");
    link.download = filename;
    link.href = href;
    link.click();
  }

  async function savePng() {
    var btn = document.getElementById("btn-save-png");
    if (btn) btn.disabled = true;
    setStatus("Generating PNG…");
    try {
      var canvas = await renderCanvas(captureRoot());
      var name = slugify(document.title) + ".png";
      downloadBlob(canvas.toDataURL("image/png"), name);
      setStatus("Saved " + name);
    } catch (err) {
      setStatus("PNG failed: " + err.message);
      console.error(err);
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  async function savePdf() {
    var btn = document.getElementById("btn-save-pdf");
    if (btn) btn.disabled = true;
    setStatus("Generating PDF…");
    try {
      if (!window.jspdf || !window.jspdf.jsPDF) {
        throw new Error("jsPDF not loaded");
      }
      var canvas = await renderCanvas(captureRoot());
      var img = canvas.toDataURL("image/png");
      var w = canvas.width;
      var h = canvas.height;
      var landscape = w > h;
      var pdf = new window.jspdf.jsPDF({
        orientation: landscape ? "landscape" : "portrait",
        unit: "px",
        format: [w, h],
        hotfixes: ["px_scaling"],
      });
      pdf.addImage(img, "PNG", 0, 0, w, h);
      var name = slugify(document.title) + ".pdf";
      pdf.save(name);
      setStatus("Saved " + name);
    } catch (err) {
      setStatus("PDF failed: " + err.message);
      console.error(err);
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function init() {
    var pngBtn = document.getElementById("btn-save-png");
    var pdfBtn = document.getElementById("btn-save-pdf");
    if (pngBtn) pngBtn.addEventListener("click", savePng);
    if (pdfBtn) pdfBtn.addEventListener("click", savePdf);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
