/* Hidden functional acceptance. Playwright package and bundled Chromium only. */
const fs = require('fs');
const http = require('http');
const path = require('path');

function inside(root, file) {
  const relative = path.relative(root, file);
  return relative !== '..' && !relative.startsWith('..' + path.sep) && !path.isAbsolute(relative);
}

function staticServer(directory) {
  const root = fs.realpathSync(directory);
  const types = {'.html':'text/html', '.js':'text/javascript', '.mjs':'text/javascript', '.css':'text/css', '.json':'application/json', '.svg':'image/svg+xml', '.png':'image/png', '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.webp':'image/webp', '.woff':'font/woff', '.woff2':'font/woff2', '.txt':'text/plain'};
  return http.createServer((request, response) => {
    try {
      let name = decodeURIComponent(request.url.split('?')[0]);
      if (name === '/') name = '/desk.html';
      const requested = path.resolve(root, '.' + name);
      if (!inside(root, requested)) throw Error('outside root');
      const file = fs.realpathSync(requested);
      if (!inside(root, file) || !fs.statSync(file).isFile()) throw Error('not a local regular file');
      response.setHeader('Content-Type', types[path.extname(file).toLowerCase()] || 'application/octet-stream');
      response.end(fs.readFileSync(file));
    } catch {
      response.writeHead(404); response.end();
    }
  });
}

async function observe(context, origin, observations) {
  context.on('page', page => {
    page.setDefaultTimeout(2500);
    page.on('pageerror', error => observations.errors.push(String(error)));
  });
  const external = url => {
    const parsed = new URL(url);
    return !['blob:', 'data:'].includes(parsed.protocol) && parsed.origin !== origin;
  };
  context.on('request', request => {
    if (external(request.url())) observations.requests.push(request.url());
  });
  await context.route('**/*', route => external(route.request().url()) ? route.abort() : route.continue());
}

async function exportByKeyboard(page, expected) {
  await page.locator('#argument').focus();
  let reachable = false;
  // The interface promises keyboard usability, not a particular focus order.
  for (let step = 0; step < 64; step++) {
    if (await page.locator('#export').evaluate(element => document.activeElement === element)) {
      reachable = true; break;
    }
    await page.keyboard.press('Tab');
  }
  if (!reachable) throw Error('export is not reachable by bounded keyboard traversal');
  const download = page.waitForEvent('download');
  await page.keyboard.press('Enter');
  const artifact = await download;
  const content = fs.readFileSync(await artifact.path(), 'utf8');
  for (const text of expected) {
    if (!content.includes(text)) throw Error('export missing ' + text);
  }
}

async function check(root, playwright) {
  const {chromium} = require(playwright);
  const server = staticServer(root);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const observations = {errors: [], requests: []};
  let browser;
  try {
    browser = await chromium.launch({headless: true});
    const desktop = await browser.newContext({acceptDownloads: true, serviceWorkers: 'block'});
    await observe(desktop, origin, observations);
    const page = await desktop.newPage();
    await page.goto(origin + '/');
    for (const id of ['river', 'estuary']) await page.locator(`[data-source="${id}"]`).click();
    const argument = 'The pilot supports protection, but seasonal floods and the small sample limit the argument.';
    const expected = [argument, 'River pilot report', 'Estuary field notes', 'A. Lin', 'B. Rao', 'https://example.invalid/river', 'https://example.invalid/estuary', 'Protected banks reduced erosion in the pilot', 'Unprotected sites lost topsoil after flooding', 'seasonal floods were not measured', 'small sample limits generalization'];
    await page.locator('#argument').fill(argument);
    await page.reload();
    await page.waitForFunction(value => document.querySelector('#argument').value === value, argument);
    await exportByKeyboard(page, expected);
    const storageState = await desktop.storageState();
    await desktop.close();
    const restored = await browser.newContext({storageState, acceptDownloads: true, viewport: {width: 390, height: 844}, reducedMotion: 'reduce', serviceWorkers: 'block'});
    await observe(restored, origin, observations);
    const narrow = await restored.newPage();
    await narrow.goto(origin + '/');
    await narrow.waitForFunction(value => document.querySelector('#argument').value === value, argument);
    // A second real download checks evidence restoration, not only draft text.
    await exportByKeyboard(narrow, expected);
    if (observations.requests.length) throw Error('offline boundary violated: ' + observations.requests.join(', '));
    if (observations.errors.length) throw Error(observations.errors.join('\n'));
    console.log(JSON.stringify({flow:'two-source-attributed-argument', reload:true, reopen:true, desktopExport:true, narrowRestoredExport:true, keyboardActivation:true, offlineBothContexts:true, aestheticAcceptance:'unverified'}));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

module.exports = {staticServer, check};
if (require.main === module) check(...process.argv.slice(2)).catch(error => {console.error(error); process.exitCode = 1;});
