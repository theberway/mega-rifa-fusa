// Uso: NODE_PATH=/opt/node-tools/node_modules node exportar.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const go = async (p, f) => { await p.goto('file://' + __dirname + '/' + f, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400); };
  let p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await go(p, 'qr-digital.html');
  await p.locator('#pieza').screenshot({ path: __dirname + '/qr-digital.png' });
  p = await b.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 3 });
  await go(p, 'qr-cartel-carta.html');
  await p.pdf({ path: __dirname + '/qr-cartel-carta.pdf', width: '8.5in', height: '11in', printBackground: true });
  await p.screenshot({ path: __dirname + '/qr-cartel-carta.png', fullPage: false });
  await go(p, 'qr-stickers-hoja.html');
  await p.pdf({ path: __dirname + '/qr-stickers-30.pdf', width: '8.5in', height: '11in', printBackground: true });
  await p.screenshot({ path: __dirname + '/qr-stickers-hoja-1.png', clip: { x: 0, y: 0, width: 816, height: 1056 } });
  await b.close();
})();
