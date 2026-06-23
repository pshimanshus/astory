import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const require = createRequire(import.meta.url);
const { chromium } = require("/Users/himanshusharma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const runId = "2026-06-14_17-51_ig-reference-concept";
const runRoot = path.join(repoRoot, "runs", runId);
const mapPath = path.join(runRoot, "planning", "exact_source_slide_map.json");
const outDir = path.join(runRoot, "corrected-exact-source-carousel");
const manifestPath = path.join(outDir, "manifest.json");
const chromePath = "/Users/himanshusharma/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell";

const map = JSON.parse(await fs.readFile(mapPath, "utf8"));
await fs.mkdir(outDir, { recursive: true });

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function segmentsHtml(slide) {
  return slide.segments.map((segment) => {
    const text = escapeHtml(segment.text).replaceAll("\n", "<br>");
    return segment.italic ? `<em>${text}</em>` : `<span>${text}</span>`;
  }).join("");
}

function sizeClass(slide) {
  const length = slide.text.length;
  if (length > 150) return "text long";
  if (length > 105) return "text medium";
  return "text";
}

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });

const rendered = [];
for (const slide of map.slides.filter((item) => item.slide <= 18)) {
  const slideNo = String(slide.slide).padStart(2, "0");
  const outputPath = path.join(outDir, `slide-${slideNo}.png`);
  const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @font-face {
      font-family: "AStorySerif";
      src: local("New York"), local("Georgia");
    }
    * { box-sizing: border-box; }
    html, body {
      width: 1080px;
      height: 1350px;
      margin: 0;
      overflow: hidden;
      background: #f8f4ec;
    }
    .slide {
      position: relative;
      width: 1080px;
      height: 1350px;
      background:
        radial-gradient(circle at 18% 28%, rgba(176, 197, 177, 0.18), transparent 20%),
        radial-gradient(circle at 82% 66%, rgba(191, 167, 148, 0.16), transparent 24%),
        linear-gradient(180deg, #fbf7ef 0%, #f5efe5 100%);
      color: #202124;
      font-family: "AStorySerif", Georgia, serif;
    }
    .paper {
      position: absolute;
      inset: 0;
      opacity: 0.19;
      background-image:
        repeating-linear-gradient(0deg, rgba(28, 26, 23, 0.028) 0, rgba(28, 26, 23, 0.028) 1px, transparent 1px, transparent 6px),
        repeating-linear-gradient(90deg, rgba(28, 26, 23, 0.02) 0, rgba(28, 26, 23, 0.02) 1px, transparent 1px, transparent 7px);
      mix-blend-mode: multiply;
    }
    .wash {
      position: absolute;
      left: 74px;
      right: 74px;
      bottom: 82px;
      height: 300px;
      opacity: 0.32;
      background:
        radial-gradient(ellipse at 20% 65%, rgba(128, 158, 145, 0.34), transparent 44%),
        radial-gradient(ellipse at 68% 46%, rgba(180, 148, 121, 0.28), transparent 46%),
        radial-gradient(ellipse at 46% 78%, rgba(108, 128, 156, 0.18), transparent 38%);
      filter: blur(12px);
    }
    .linework {
      position: absolute;
      left: 86px;
      right: 86px;
      bottom: 94px;
      height: 252px;
      border-bottom: 2px solid rgba(40, 38, 34, 0.22);
      opacity: 0.7;
    }
    .linework:before,
    .linework:after {
      content: "";
      position: absolute;
      bottom: 0;
      border: 2px solid rgba(40, 38, 34, 0.18);
      border-top: 0;
      border-radius: 0 0 46% 46%;
    }
    .linework:before {
      left: 92px;
      width: 246px;
      height: 128px;
      transform: rotate(-3deg);
    }
    .linework:after {
      right: 116px;
      width: 230px;
      height: 118px;
      transform: rotate(3deg);
    }
    .brand {
      position: absolute;
      top: 45px;
      right: 58px;
      font: 30px "Bradley Hand", "Marker Felt", cursive;
      letter-spacing: 0;
      color: rgba(27, 27, 27, 0.72);
    }
    .text-wrap {
      position: absolute;
      left: 108px;
      right: 108px;
      top: 206px;
      bottom: 360px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    .text {
      width: 100%;
      font-size: 74px;
      line-height: 1.12;
      font-weight: 650;
      letter-spacing: 0;
      text-wrap: balance;
    }
    .text.medium {
      font-size: 63px;
      line-height: 1.15;
    }
    .text.long {
      font-size: 54px;
      line-height: 1.18;
    }
    em {
      font-style: italic;
      font-weight: 520;
    }
    .footer {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 42px;
      text-align: center;
      font: 26px "Bradley Hand", "Marker Felt", cursive;
      color: rgba(27, 27, 27, 0.46);
    }
  </style>
</head>
<body>
  <main class="slide">
    <div class="paper"></div>
    <div class="brand">@a.storyof.two</div>
    <div class="text-wrap"><div class="${sizeClass(slide)}">${segmentsHtml(slide)}</div></div>
    <div class="wash"></div>
    <div class="linework"></div>
    <div class="footer">a story of two</div>
  </main>
</body>
</html>`;
  await page.setContent(html, { waitUntil: "load" });
  await page.screenshot({ path: outputPath, type: "png" });
  rendered.push({
    slide: slide.slide,
    file: path.basename(outputPath),
    source_image: slide.source_image,
    on_image_text: slide.text,
    pixel_width: 1080,
    pixel_height: 1350
  });
}

await browser.close();

const manifest = {
  schema_version: "1.0",
  run_id: runId,
  created_at: new Date().toISOString(),
  correction: "Exact source text rendered deterministically in A Story visual/design theme. Previous invented variant package remains rejected.",
  format: {
    pixel_width: 1080,
    pixel_height: 1350
  },
  rendered_slide_count: rendered.length,
  slides: rendered,
  excluded_source_slides: map.excluded_from_render
};
await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2) + "\n");
console.log(JSON.stringify({ outDir, manifestPath, rendered: rendered.length }, null, 2));
