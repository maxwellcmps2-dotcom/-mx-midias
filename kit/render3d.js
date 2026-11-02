// uso: node render3d.js <pasta_raiz> <arquivo.html> <pasta_frames> <segundos> [fps]
// Serve a pasta via HTTP local (módulos ES/three.js não carregam via file://) e captura quadro a quadro.
const { chromium } = require('playwright');
const http = require('http'), path = require('path'), fs = require('fs');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.css': 'text/css' };
(async () => {
  const [root, html, out, secs, fpsArg] = process.argv.slice(2);
  const fps = Number(fpsArg || 30), total = Math.round(Number(secs) * fps);
  fs.mkdirSync(out, { recursive: true });
  const srv = http.createServer((req, res) => {
    const f = path.join(path.resolve(root), decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(f, (e, d) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); res.end(d); });
  }).listen(0);
  const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('console', m => { if (m.type() === 'error') console.log('page error:', m.text()); });
  pg.on('pageerror', e => console.log('page exception:', e.message));
  await pg.goto(`http://localhost:${port}/${html}`);
  await pg.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  await pg.evaluate(() => document.fonts.ready);
  for (let i = 0; i < total; i++) {
    await pg.evaluate(t => window.setT(t), i / fps);
    await pg.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close(); srv.close();
  console.log('frames:', total);
})();
