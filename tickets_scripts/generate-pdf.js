/**
 * Generates Music Bingo tickets as HTML or PDF.
 * - 2 tickets per A4 landscape page (side by side)
 * - 0 margins for print
 *
 * Usage (run from project root or from apps/):
 *   node apps/generate-pdf.js [TEMPLATE_NAME] -html [-o <file_name>]   Save output/tickets_final/tickets.html (default)
 *   node apps/generate-pdf.js [TEMPLATE_NAME] -pdf  [-o <file_name>]    Save output/tickets_final/tickets.pdf (default)
 *   Or: cd apps && node generate-pdf.js -html
 *
 * Examples:
 *   node apps/generate-pdf.js -html
 *   node apps/generate-pdf.js 60_70_90.jpeg -pdf -o bilete_music_bingo
 */

const fs = require('fs');
const path = require('path');

// Paths under the app folder (same as index_real.py output)
const ticketsDir = path.join(__dirname, 'output', 'tickets');
const outputDir = path.join(__dirname, 'output', 'tickets_final');

// Parse CLI: node generate-pdf.js [TEMPLATE_NAME] (-html | -pdf) [-o <file_name>]
const args = process.argv.slice(2);
const outputFormat = args.includes('-pdf') ? 'pdf' : 'html';
const oIndex = args.indexOf('-o');
let outputBaseName = 'tickets';
if (oIndex !== -1 && args[oIndex + 1]) {
  outputBaseName = args[oIndex + 1];
  if (path.extname(outputBaseName)) outputBaseName = path.basename(outputBaseName, path.extname(outputBaseName));
}
const outputHtmlFile = path.join(outputDir, outputBaseName + '.html');
const outputPdfFile = path.join(outputDir, outputBaseName + '.pdf');

// Template: first non-option arg that is not the value of -o
const restArgs = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '-o') { i++; continue; }
  restArgs.push(args[i]);
}
const templateName = restArgs.find(a => !a.startsWith('-')) || process.env.TEMPLATE || 'oneH';
const hasExtension = path.extname(templateName).length > 0;
const templateDir = path.join(__dirname, 'sources', 'template');
const templateBgPath = path.join(templateDir, hasExtension ? templateName : `${templateName}.JPG`);

// === Helpers ===
function escapeHtml(unsafe) {
  return String(unsafe || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function ensureDirExists(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

// === Main ===
async function main() {
  if (!fs.existsSync(ticketsDir)) {
    console.error('❌ No tickets folder found at', ticketsDir);
    process.exit(1);
  }

  const files = fs.readdirSync(ticketsDir)
    .filter(f => f.toLowerCase().endsWith('.json'))
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

  if (files.length === 0) {
    console.error('❌ No .json tickets found in', ticketsDir);
    process.exit(1);
  }

  ensureDirExists(outputDir);

  // Read background image as Base64 (same size & grid as other templates)
  let bgDataUri = '';
  let resolvedPath = templateBgPath;
  if (!fs.existsSync(resolvedPath) && !hasExtension) {
    const pngPath = path.join(templateDir, `${templateName}.png`);
    if (fs.existsSync(pngPath)) resolvedPath = pngPath;
  }
  if (fs.existsSync(resolvedPath)) {
    const buf = fs.readFileSync(resolvedPath);
    const mime = buf[0] === 0xff && buf[1] === 0xd8 ? 'image/jpeg' : 'image/png';
    bgDataUri = `data:${mime};base64,${buf.toString('base64')}`;
  } else {
    console.warn('⚠️ Background not found at', templateBgPath, ', using blank background.');
  }

  // Load ticket data (number tickets 1, 2, 3, ... by order in folder)
  const tickets = files.map((f, i) => {
    const data = JSON.parse(fs.readFileSync(path.join(ticketsDir, f), 'utf8'));
    const songs = (data.songs || []).slice(0, 9);
    while (songs.length < 9) songs.push({ title: '', artists: '' });
    return { id: i + 1, songs };
  });

  // Build HTML
  const html = buildHtmlPage(tickets, bgDataUri);

  if (outputFormat === 'html') {
    fs.writeFileSync(outputHtmlFile, html, 'utf8');
    console.log(`✅ Generated ${outputHtmlFile} (template: ${templateName})\n👉 Open in browser to preview/print.`);
  } else {
    const puppeteer = require('puppeteer');
    const execPath = getChromeExecutablePath();
    try {
      const browser = await puppeteer.launch({
        headless: 'new',
        ...(execPath && { executablePath: execPath })
      });
      const page = await browser.newPage();
      // Match A4 landscape so vw units (e.g. ticket number) scale correctly in PDF
      await page.setViewport({ width: 1122, height: 794 }); // 297mm × 210mm @ 96dpi
      await page.setContent(html, { waitUntil: 'networkidle0' });
      await page.pdf({
        path: outputPdfFile,
        format: 'A4',
        landscape: true,
        margin: { top: 0, right: 0, bottom: 0, left: 0 },
        printBackground: true
      });
      await browser.close();
      console.log(`✅ Generated ${outputPdfFile} (template: ${templateName})`);
    } catch (err) {
      if (err.message && err.message.includes('Could not find Chrome')) {
        console.error('❌ PDF generation needs Chrome/Chromium (Puppeteer does not use Firefox).');
        console.error('   Option 1: Install Chrome for Puppeteer:  npx puppeteer browsers install chrome');
        console.error('   Option 2: Generate HTML and print to PDF from your browser:');
        console.error('             node generate-pdf.js ' + (templateName !== 'oneH' ? templateName + ' ' : '') + '-html');
        console.error('             Then open output/tickets_final/tickets.html in Firefox → Print → Save to PDF.');
        process.exit(1);
      }
      throw err;
    }
  }
}

function getChromeExecutablePath() {
  const { execSync } = require('child_process');
  const candidates = ['chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable'];
  for (const name of candidates) {
    try {
      const path = execSync('which ' + name, { encoding: 'utf8' }).trim();
      if (path && fs.existsSync(path)) return path;
    } catch (_) {}
  }
  return null;
}

// === Build HTML Page ===
function buildHtmlPage(tickets, bgDataUri) {
  const css = `
    @page { size: A4 landscape; margin: 0; }
    html, body {
      margin: 0;
      padding: 0;
      background: #eee;
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .page {
      width: 297mm;
      height: 210mm;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: white;
      page-break-after: always;
      box-sizing: border-box;
      padding: 0;
    }

    .ticket {
      position: relative;
      width: 50%;
      height: 98.5%;
      aspect-ratio: 768 / 1086;
      background-image: url("${bgDataUri}");
      background-repeat: no-repeat;
      background-size: contain;
      background-position: center;
      box-sizing: border-box;
    }

    .grid3 {
      position: absolute;
      left: 7.7%;
      top: 21.9%;
      width: 83.7%;
      height: 58.2%;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 1fr);
      align-items: center;
      justify-items: center;
      pointer-events: none;
    }

    .cell {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 1%;
      box-sizing: border-box;
      text-align: center;
      color: #111;
      background: transparent;
      overflow: hidden;
    }

    .song-title {
      font-size: 1.4vw;
      font-weight: 800;
      line-height: 1.05;
      margin-bottom: 0;
      word-break: break-word;
      hyphens: auto;
      flex-shrink: 1;
      min-height: 0;
    }

    .song-artists {
      font-size: 1.4vw;
      font-weight: 400;
      line-height: 1.05;
      word-break: break-word;
      hyphens: auto;
      flex-shrink: 1;
      min-height: 0;
    }

    /* Long title/artists: use smaller font so text fits in the square */
    .cell.cell--long .song-title,
    .cell.cell--long .song-artists {
      font-size: 1.1vw;
      line-height: 1.03;
    }

    .ticket-number {
      position: absolute;
      left: 22.7%;
      top: 16.5%;
      font-size: 18.5px;
      font-weight: 800;
      line-height: 1;
      color: #c78d37;
      font-family: "Helvetica Now", "Helvetica Neue", Helvetica, Arial, sans-serif;
      -webkit-text-stroke: 0.5px #000;
      text-shadow: 1px 1px 1px rgba(0, 45, 70, 0.2);
      pointer-events: none;
      white-space: nowrap;
    }

    @media print {
      body { background: white; }
      .page { margin: 0; box-shadow: none; }
    }
  `;

  // Chunk tickets into groups of 2 per page (side by side)
  const pages = [];
  for (let i = 0; i < tickets.length; i += 2) {
    const chunk = tickets.slice(i, i + 2);
    const pageHtml = chunk.map(t => {
      const cells = t.songs.map(s => {
        const title = String(s.title || '').trim();
        const artists = String(s.artists || '').trim().replace(/;\s*/g, ' • ');
        const totalLen = title.length + artists.length;
        const longClass = totalLen > 28 ? ' cell--long' : '';
        return `
        <div class="cell${longClass}">
          <div class="song-title">${escapeHtml(title)}</div>
          <div class="song-artists">${escapeHtml(artists)}</div>
        </div>
      `;
      }).join('');

      return `
        <div class="ticket">
          <div class="ticket-number">${escapeHtml(t.id)}</div>
          <div class="grid3">${cells}</div>
        </div>
      `;
    }).join('');

    pages.push(`<div class="page">${pageHtml}</div>`);
  }

  return `
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Music Bingo Tickets</title>
        <style>${css}</style>
      </head>
      <body>
        ${pages.join('\n')}
      </body>
    </html>
  `;
}

main();
