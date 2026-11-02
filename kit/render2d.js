// uso: node render.js <arquivo.html> <pasta_frames> <segundos> [fps]
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [html, out, secs, fpsArg] = process.argv.slice(2);
  const fps = Number(fpsArg || 30), total = Math.round(Number(secs) * fps);
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await pg.goto('file://' + path.resolve(html));
  await pg.evaluate(() => document.fonts.ready);
  for (let i = 0; i < total; i++) {
    await pg.evaluate(t => window.setT(t), i / fps);
    await pg.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
  console.log('frames:', total);
})();
