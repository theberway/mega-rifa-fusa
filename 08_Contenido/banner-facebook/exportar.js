// Uso: NODE_PATH=/opt/node-tools/node_modules node exportar.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 820, height: 312 }, deviceScaleFactor: 2 });
  await p.goto('file://' + __dirname + '/banner-facebook.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.locator('#banner').screenshot({ path: __dirname + '/banner-facebook.png' });
  await b.close();
})();
