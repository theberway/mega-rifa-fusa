// Uso: NODE_PATH=/opt/node-tools/node_modules node exportar.js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + __dirname + '/historia-premio.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  await p.locator('#pieza').screenshot({ path: __dirname + '/historia-premio.png' });
  await b.close();
})();
